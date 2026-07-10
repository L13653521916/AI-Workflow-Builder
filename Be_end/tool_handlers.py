"""Built-in tool handlers for test / workflow execution."""

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any

DEFAULT_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

HTTP_ERROR_HINTS = {
    403: "目标站点拒绝访问，可能需要登录或 API Key",
    412: "目标站点启用了反爬策略（常见于 B站、微博等），需浏览器 Cookie 或专用 API，并非工具故障",
    429: "请求过于频繁，请稍后重试",
}


def handle_web_search(params: dict) -> Any:
    query = params.get("query", "")
    if not query:
        raise ValueError("缺少参数 query")
    return {
        "query": query,
        "results": [
            {"title": f"关于「{query}」的搜索结果 1", "snippet": "这是模拟搜索摘要，Phase 7 可接入真实搜索 API"},
            {"title": f"关于「{query}」的搜索结果 2", "snippet": "更多相关信息..."},
        ],
    }


def handle_code_exec(params: dict) -> Any:
    code = params.get("code", "")
    if not code:
        raise ValueError("缺少参数 code")
    if len(code) > 10000:
        raise ValueError("代码长度不能超过 10000 字符")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=tempfile.gettempdir(),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "success": proc.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        raise ValueError("代码执行超时（15 秒）")
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def handle_http_request(params: dict) -> Any:
    url = params.get("url", "")
    if not url:
        raise ValueError("缺少参数 url")
    method = params.get("method", "GET").upper()
    if method not in ("GET", "POST"):
        raise ValueError("仅支持 GET / POST 请求")

    headers = {**DEFAULT_HTTP_HEADERS}
    user_headers = params.get("headers") or {}
    if isinstance(user_headers, str):
        try:
            user_headers = json.loads(user_headers)
        except json.JSONDecodeError:
            user_headers = {}
    headers.update({str(k): str(v) for k, v in user_headers.items()})

    body_data = params.get("body")
    data = None
    if body_data is not None and method == "POST":
        data = json.dumps(body_data).encode("utf-8") if isinstance(body_data, dict) else str(body_data).encode("utf-8")
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                parsed_body = json.loads(raw)
            except json.JSONDecodeError:
                parsed_body = raw[:2000] if len(raw) > 2000 else raw
            return {
                "status": resp.status,
                "url": url,
                "body": parsed_body,
            }
    except urllib.error.HTTPError as e:
        hint = HTTP_ERROR_HINTS.get(e.code, "")
        return {
            "status": e.code,
            "url": url,
            "error": str(e),
            "hint": hint,
        }
    except Exception as e:
        raise ValueError(f"HTTP 请求失败: {e}")


def handle_json_parse(params: dict) -> Any:
    text = params.get("text", "")
    if not text:
        raise ValueError("缺少参数 text")
    try:
        parsed = json.loads(text)
        return {"valid": True, "data": parsed}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": str(e)}


def handle_text_split(params: dict) -> Any:
    text = params.get("text", "")
    delimiter = params.get("delimiter", "\n")
    if not text:
        raise ValueError("缺少参数 text")
    parts = text.split(delimiter)
    return {"count": len(parts), "parts": parts}


def handle_string_replace(params: dict) -> Any:
    text = params.get("text", "")
    old = params.get("old", "")
    new = params.get("new", "")
    if not text:
        raise ValueError("缺少参数 text")
    result = text.replace(old, new)
    return {"result": result, "replaced_count": text.count(old) if old else 0}


def handle_current_time(params: dict) -> Any:
    fmt = params.get("format", "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    return {
        "timestamp": now.timestamp(),
        "formatted": now.strftime(fmt),
        "iso": now.isoformat(),
    }


def handle_regex_match(params: dict) -> Any:
    text = params.get("text", "")
    pattern = params.get("pattern", "")
    if not text or not pattern:
        raise ValueError("缺少参数 text 或 pattern")
    matches = re.findall(pattern, text)
    return {"pattern": pattern, "matches": matches, "count": len(matches)}


def handle_text_length(params: dict) -> Any:
    text = params.get("text", "")
    return {
        "chars": len(text),
        "lines": len(text.splitlines()),
        "words": len(text.split()),
    }


HANDLERS = {
    "web_search": handle_web_search,
    "code_exec": handle_code_exec,
    "http_request": handle_http_request,
    "json_parse": handle_json_parse,
    "text_split": handle_text_split,
    "string_replace": handle_string_replace,
    "current_time": handle_current_time,
    "regex_match": handle_regex_match,
    "text_length": handle_text_length,
}

HANDLER_LABELS = {
    "web_search": "Web 搜索",
    "code_exec": "Python 代码执行",
    "http_request": "HTTP 请求",
    "json_parse": "JSON 解析",
    "text_split": "文本分割",
    "string_replace": "字符串替换",
    "current_time": "获取当前时间",
    "regex_match": "正则匹配",
    "text_length": "文本统计",
}
