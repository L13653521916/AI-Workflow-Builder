from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Tool
from schemas import ToolResponse, ToolTestRequest, ToolCreate
from security import get_current_user
from models import User
from tool_handlers import HANDLERS, HANDLER_LABELS

router = APIRouter(prefix="/tools", tags=["tools"])

BUILTIN_TOOLS = [
    {
        "name": "web_search",
        "description": "搜索互联网获取信息（当前为模拟结果，可接入真实搜索 API）",
        "category": "search",
        "handler_name": "web_search",
        "schema_json": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "搜索关键词"}},
            "required": ["query"],
        },
    },
    {
        "name": "code_exec",
        "description": "执行 Python 代码（支持多行、print 输出，超时 15 秒）",
        "category": "code",
        "handler_name": "code_exec",
        "schema_json": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python 代码，如 print('hello')"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "http_request",
        "description": "发送 HTTP 请求（GET/POST），自动附带浏览器 User-Agent",
        "category": "api",
        "handler_name": "http_request",
        "schema_json": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "请求 URL"},
                "method": {"type": "string", "default": "GET", "description": "GET 或 POST"},
                "headers": {"type": "object", "description": "额外请求头（JSON）"},
                "body": {"type": "object", "description": "POST 请求体（JSON）"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "json_parse",
        "description": "解析 JSON 字符串并验证格式",
        "category": "data",
        "handler_name": "json_parse",
        "schema_json": {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "JSON 字符串"}},
            "required": ["text"],
        },
    },
    {
        "name": "text_split",
        "description": "按分隔符拆分文本",
        "category": "text",
        "handler_name": "text_split",
        "schema_json": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待拆分文本"},
                "delimiter": {"type": "string", "default": "\\n", "description": "分隔符"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "string_replace",
        "description": "在文本中查找并替换字符串",
        "category": "text",
        "handler_name": "string_replace",
        "schema_json": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "原文本"},
                "old": {"type": "string", "description": "要替换的内容"},
                "new": {"type": "string", "description": "替换为"},
            },
            "required": ["text", "old"],
        },
    },
    {
        "name": "regex_match",
        "description": "使用正则表达式提取文本中的匹配项",
        "category": "text",
        "handler_name": "regex_match",
        "schema_json": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待匹配文本"},
                "pattern": {"type": "string", "description": "正则表达式"},
            },
            "required": ["text", "pattern"],
        },
    },
    {
        "name": "text_length",
        "description": "统计文本字符数、行数、词数",
        "category": "text",
        "handler_name": "text_length",
        "schema_json": {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "待统计文本"}},
            "required": ["text"],
        },
    },
    {
        "name": "current_time",
        "description": "获取当前系统时间",
        "category": "utility",
        "handler_name": "current_time",
        "schema_json": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "default": "%Y-%m-%d %H:%M:%S",
                    "description": "时间格式（可选）",
                },
            },
        },
    },
]

BUILTIN_NAMES = {t["name"] for t in BUILTIN_TOOLS}


def seed_tools(db: Session):
    for data in BUILTIN_TOOLS:
        existing = db.query(Tool).filter(Tool.name == data["name"]).first()
        if not existing:
            db.add(Tool(**data))
        else:
            existing.description = data["description"]
            existing.schema_json = data["schema_json"]
            existing.category = data["category"]
    db.commit()


@router.get("/handlers")
def list_handlers(current_user: User = Depends(get_current_user)):
  """返回可复用的 handler 列表，供自定义工具选择"""
  return [
    {"name": k, "label": HANDLER_LABELS.get(k, k)}
    for k in HANDLERS.keys()
  ]


@router.get("", response_model=List[ToolResponse])
def list_tools(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seed_tools(db)
    q = db.query(Tool).filter(Tool.is_active == True)
    if category:
        q = q.filter(Tool.category == category)
    tools = q.order_by(Tool.category, Tool.name).all()
    return [ToolResponse.from_orm_model(t) for t in tools]


@router.post("", response_model=ToolResponse, status_code=201)
def create_custom_tool(
    body: ToolCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.handler_name not in HANDLERS:
        raise HTTPException(status_code=400, detail=f"不支持的 handler: {body.handler_name}")
    if db.query(Tool).filter(Tool.name == body.name).first():
        raise HTTPException(status_code=400, detail="工具标识名已存在，请换一个")

    tool = Tool(
        name=body.name,
        description=body.description,
        category=body.category or "custom",
        handler_name=body.handler_name,
        schema_json=body.schema_json or HANDLERS_SCHEMA_DEFAULT(body.handler_name),
        is_active=True,
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return ToolResponse.from_orm_model(tool)


def HANDLERS_SCHEMA_DEFAULT(handler_name: str) -> dict:
    builtin = next((t for t in BUILTIN_TOOLS if t["handler_name"] == handler_name), None)
    return builtin["schema_json"] if builtin else {"type": "object", "properties": {}}


@router.delete("/{tool_id}")
def delete_custom_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool.name in BUILTIN_NAMES:
        raise HTTPException(status_code=400, detail="内置工具不可删除")
    db.delete(tool)
    db.commit()
    return {"detail": "ok"}


@router.get("/{tool_id}", response_model=ToolResponse)
def get_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seed_tools(db)
    tool = db.query(Tool).filter(Tool.id == tool_id, Tool.is_active == True).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return ToolResponse.from_orm_model(tool)


@router.post("/{tool_id}/test")
def test_tool(
    tool_id: int,
    body: ToolTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seed_tools(db)
    tool = db.query(Tool).filter(Tool.id == tool_id, Tool.is_active == True).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    handler = HANDLERS.get(tool.handler_name)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Handler '{tool.handler_name}' not implemented")

    try:
        result = handler(body.params)
        return {"success": True, "result": result}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
