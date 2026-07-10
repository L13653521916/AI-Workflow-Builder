"""Workflow graph execution engine."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from tool_handlers import HANDLERS
from database import SessionLocal
from model_runtime import resolve_model_profile, execute_llm_with_profile


def _node_config(node: dict) -> dict:
    return node.get("config") or {}


def _node_label(node: dict) -> str:
    return node.get("label") or node.get("type") or node.get("id", "")


def build_execution_order(nodes: List[dict], edges: List[dict]) -> List[dict]:
    if not nodes:
        raise ValueError("工作流没有节点")

    node_map = {n["id"]: n for n in nodes}
    start_nodes = [n for n in nodes if n.get("type") == "start"]
    if not start_nodes:
        raise ValueError("工作流缺少起始节点")

    out_edges: Dict[str, List[dict]] = defaultdict(list)
    for e in edges:
        out_edges[e["source"]].append(e)

    order: List[dict] = []
    visited: set[str] = set()
    queue = [start_nodes[0]["id"]]

    while queue:
        nid = queue.pop(0)
        if nid in visited or nid not in node_map:
            continue
        visited.add(nid)
        order.append(node_map[nid])
        for e in out_edges.get(nid, []):
            target = e["target"]
            if target not in visited:
                queue.append(target)

    return order


def _render_template(template: str, data: Any) -> str:
    text = str(data)
    return template.replace("{{input}}", text).replace("{{output}}", text)


def execute_node(node: dict, input_data: Any, context: dict) -> Any:
    ntype = node.get("type")
    config = _node_config(node)

    if ntype == "start":
        if isinstance(input_data, dict):
            return input_data
        return {"input": input_data}

    if ntype == "llm":
        profile_id = config.get("modelProfileId")
        if profile_id is not None:
            try:
                profile_id = int(profile_id)
            except (TypeError, ValueError):
                profile_id = None

        profile = None
        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("无法加载模型配置：缺少用户上下文")

        db = SessionLocal()
        profile_data = None
        try:
            profile = resolve_model_profile(db, user_id, profile_id)
            if profile_id and not profile:
                raise ValueError(f"模型配置 #{profile_id} 不存在或无权访问")
            if profile:
                profile_data = {
                    "id": profile.id,
                    "name": profile.name,
                    "provider": profile.provider,
                    "base_url": profile.base_url,
                    "api_key": profile.api_key,
                    "model_id": profile.model_id,
                    "config_json": profile.config_json,
                }
        finally:
            db.close()

        content, trace = execute_llm_with_profile(config, input_data, profile_data, context)

        context["last_trace"] = trace
        return content

    if ntype == "rag":
        query = str(input_data) if not isinstance(input_data, dict) else json.dumps(input_data, ensure_ascii=False)
        kb_id = config.get("knowledgeBase")
        top_k = config.get("topK", 3)
        return {
            "query": query,
            "knowledge_base_id": kb_id,
            "top_k": top_k,
            "chunks": [
                {
                    "content": f"[模拟检索] 来自知识库 #{kb_id or '未配置'} 的相关片段 {i + 1}",
                    "score": round(0.9 - i * 0.1, 2),
                }
                for i in range(min(top_k, 3))
            ],
            "note": "RAG 向量化检索将在后续版本接入，当前为模拟结果",
        }

    if ntype == "tool":
        tool_name = config.get("tool")
        if not tool_name:
            raise ValueError("工具节点未选择工具")
        handler = HANDLERS.get(tool_name)
        if not handler:
            raise ValueError(f"未知工具: {tool_name}")

        params_raw = config.get("toolParams", "{}")
        if isinstance(params_raw, str):
            try:
                params = json.loads(params_raw) if params_raw.strip() else {}
            except json.JSONDecodeError:
                params = {}
        else:
            params = params_raw or {}

        if tool_name == "http_request" and config.get("toolUrl") and "url" not in params:
            params["url"] = config.get("toolUrl")

        if isinstance(input_data, dict) and "input" not in params:
            params.setdefault("text", json.dumps(input_data, ensure_ascii=False))
        elif "text" not in params and "query" not in params and "code" not in params:
            params.setdefault("text", str(input_data))

        return handler(params)

    if ntype == "condition":
        expr = config.get("condition") or "True"
        text = str(input_data)
        try:
            passed = bool(eval(expr, {"__builtins__": {}}, {"output": input_data, "text": text, "len": len}))
        except Exception:
            passed = len(text) > 0
        return {"passed": passed, "input": input_data, "expression": expr}

    if ntype == "end":
        fmt = config.get("outputFormat", "raw")
        template = config.get("outputTemplate") or ""
        if template:
            result = _render_template(template, input_data)
        elif fmt == "json" and not isinstance(input_data, str):
            result = json.dumps(input_data, ensure_ascii=False, indent=2)
        else:
            result = str(input_data)
        return {"format": fmt, "result": result}

    return input_data


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
