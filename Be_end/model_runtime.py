"""Resolve model profiles and run LLM calls with saved user settings."""

from __future__ import annotations

import json
import time
from typing import Any, List, Optional, Tuple

from openai import OpenAI
from sqlalchemy.orm import Session

from config import settings
from models import ModelProfile
from schemas import DEFAULT_MODEL_CONFIG


def merge_profile_config(config_json: dict | None) -> dict:
    merged = {**DEFAULT_MODEL_CONFIG}
    if not config_json:
        return merged
    for section, values in config_json.items():
        if section in merged and isinstance(values, dict):
            merged[section] = {**merged[section], **values}
        else:
            merged[section] = values
    return merged


def resolve_model_profile(
    db: Session,
    user_id: int,
    profile_id: Optional[int] = None,
) -> Optional[ModelProfile]:
    if profile_id:
        profile = (
            db.query(ModelProfile)
            .filter(ModelProfile.id == profile_id, ModelProfile.user_id == user_id)
            .first()
        )
        if profile:
            return profile

    return (
        db.query(ModelProfile)
        .filter(ModelProfile.user_id == user_id, ModelProfile.is_default == True)
        .first()
    )


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 2)


def _truncate_text(text: str, max_tokens: int) -> str:
    max_chars = max_tokens * 2
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def _extract_rag_chunks(input_data: Any) -> List[str]:
    if isinstance(input_data, dict) and "chunks" in input_data:
        chunks = input_data.get("chunks") or []
        return [
            c.get("content", str(c)) if isinstance(c, dict) else str(c)
            for c in chunks
        ]
    return []


def _build_messages_for_profile(
    node_config: dict,
    input_data: Any,
    profile_config: dict,
    message_history: Optional[List[dict]] = None,
) -> Tuple[List[dict], dict]:
    ctx_cfg = profile_config.get("context", {})
    hist_cfg = profile_config.get("history", {})
    max_context = int(ctx_cfg.get("maxContextTokens", 8192))

    system_ratio = int(ctx_cfg.get("systemTokenRatio", 10))
    user_ratio = int(ctx_cfg.get("userTokenRatio", 60))
    rag_ratio = int(ctx_cfg.get("ragTokenRatio", 20))
    compression = ctx_cfg.get("compressionStrategy", "none")

    system_budget = max(256, max_context * system_ratio // 100)
    user_budget = max(512, max_context * user_ratio // 100)
    rag_budget = max(256, max_context * rag_ratio // 100)

    user_text = node_config.get("prompt") or "{{input}}"
    if isinstance(input_data, dict):
        user_text = user_text.replace("{{input}}", json.dumps(input_data, ensure_ascii=False))
    else:
        user_text = user_text.replace("{{input}}", str(input_data))

    rag_chunks = _extract_rag_chunks(input_data)
    if rag_chunks:
        rag_text = "\n\n".join(rag_chunks)
        rag_text = _truncate_text(rag_text, rag_budget)
        user_text = f"【检索上下文】\n{rag_text}\n\n【用户任务】\n{user_text}"

    system_prompt = node_config.get("systemPrompt") or ""
    if system_prompt:
        system_prompt = _truncate_text(system_prompt, system_budget)

    if _estimate_tokens(user_text) > user_budget:
        user_text = _truncate_text(user_text, user_budget)
        if compression == "summarize":
            user_text += "\n\n[内容已按摘要策略压缩]"

    messages: List[dict] = []
    history = message_history or []
    strategy = hist_cfg.get("strategy", "sliding_window")
    max_messages = int(hist_cfg.get("maxMessages", 20))
    window_size = int(hist_cfg.get("windowSize", 10))

    if strategy == "sliding_window" and history:
        messages.extend(history[-window_size:])
    elif strategy == "summarize" and history:
        summary = " | ".join(
            f"{m.get('role', 'user')}: {str(m.get('content', ''))[:80]}"
            for m in history[-max_messages:]
        )
        messages.append({"role": "system", "content": f"历史摘要: {_truncate_text(summary, 512)}"})
    elif strategy == "vector_retrieval" and history:
        query = user_text[:200]
        matched = [m for m in history if query[:30] in str(m.get("content", ""))]
        messages.extend((matched or history)[-window_size:])

    if system_prompt:
        if messages and messages[0].get("role") == "system":
            messages[0] = {"role": "system", "content": system_prompt + "\n" + messages[0]["content"]}
        else:
            messages.insert(0, {"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_text})

    applied = {
        "maxContextTokens": max_context,
        "compressionStrategy": compression,
        "historyStrategy": strategy,
        "estimatedInputTokens": _estimate_tokens(system_prompt) + _estimate_tokens(user_text),
        "ragChunksInjected": len(rag_chunks),
        "historyMessagesUsed": len(history),
        "tokenBudget": {"system": system_budget, "user": user_budget, "rag": rag_budget},
    }
    return messages, applied


def _profile_get(profile: Any, field: str, default=None):
    if profile is None:
        return default
    if isinstance(profile, dict):
        return profile.get(field, default)
    return getattr(profile, field, default)


def execute_llm_with_profile(
    node_config: dict,
    input_data: Any,
    profile: Optional[Any],
    context: dict,
) -> Tuple[str, dict]:
    """Run LLM using model profile (or fallback to server config). Returns (text, trace)."""
    agent_cfg = DEFAULT_MODEL_CONFIG["agent"]
    obs_cfg = DEFAULT_MODEL_CONFIG["observability"]
    profile_name = "服务端默认"
    base_url = settings.DASHSCOPE_BASE_URL
    api_key = settings.DASHSCOPE_API_KEY
    model_id = node_config.get("model") or settings.DASHSCOPE_MODEL
    profile_config = DEFAULT_MODEL_CONFIG

    if profile:
        profile_name = _profile_get(profile, "name", "未命名")
        base_url = _profile_get(profile, "base_url")
        api_key = _profile_get(profile, "api_key")
        model_id = _profile_get(profile, "model_id")
        profile_config = merge_profile_config(_profile_get(profile, "config_json"))
        agent_cfg = profile_config.get("agent", agent_cfg)
        obs_cfg = profile_config.get("observability", obs_cfg)

    messages, applied = _build_messages_for_profile(
        node_config,
        input_data,
        profile_config,
        context.get("message_history"),
    )

    temperature = float(node_config.get("temperature", 0.7))
    node_max_tokens = int(node_config.get("maxTokens", 2048))
    ctx_max = int(profile_config.get("context", {}).get("maxContextTokens", 8192))
    max_tokens = min(node_max_tokens, max(256, ctx_max // 4))

    client = OpenAI(api_key=api_key, base_url=base_url)
    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    latency_ms = round((time.perf_counter() - start) * 1000, 1)
    content = response.choices[0].message.content or ""

    history = context.setdefault("message_history", [])
    history.append({"role": "user", "content": messages[-1]["content"]})
    history.append({"role": "assistant", "content": content})
    max_hist = int(profile_config.get("history", {}).get("maxMessages", 20))
    if len(history) > max_hist:
        context["message_history"] = history[-max_hist:]

    trace = {
        "profileId": _profile_get(profile, "id"),
        "profileName": profile_name,
        "provider": _profile_get(profile, "provider", "server_default") if profile else "server_default",
        "baseUrl": base_url,
        "modelId": model_id,
        "agentMode": agent_cfg.get("mode", "tool_calling"),
        "maxIterations": agent_cfg.get("maxIterations", 10),
        "toolWhitelist": agent_cfg.get("toolWhitelist", []),
        "enableTracing": bool(obs_cfg.get("enableTracing", True)),
        "logToolCalls": bool(obs_cfg.get("logToolCalls", True)),
        "latencyMs": latency_ms,
        "strategiesApplied": applied,
        "usage": {
            "prompt_tokens": getattr(response.usage, "prompt_tokens", None) if response.usage else None,
            "completion_tokens": getattr(response.usage, "completion_tokens", None) if response.usage else None,
        },
    }
    context["last_trace"] = trace
    return content, trace
