import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from openai import OpenAI

from database import get_db, SessionLocal
from config import settings
from models import User, Conversation, Message
from schemas import (
    ConversationCreate, ConversationResponse, ConversationDetail,
    MessageCreate, MessageResponse,
)
from security import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

llm_client = OpenAI(
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
)


# ── Conversation CRUD ─────────────────────────────────
@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(func.coalesce(Conversation.updated_at, Conversation.created_at).desc())
        .all()
    )
    return convs


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
def create_conversation(
    body: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = Conversation(user_id=current_user.id, title=body.title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/conversations/{conv_id}", response_model=ConversationDetail)
def get_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conv_id}")
def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"detail": "ok"}


# ── Send Message (SSE streaming) ──────────────────────
@router.post("/conversations/{conv_id}/messages")
def send_message(
    conv_id: int,
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 1. 持久化用户消息
    user_msg = Message(conversation_id=conv_id, role="user", content=body.content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 2. 自动以第一条消息作为对话标题
    msg_count = db.query(Message).filter(Message.conversation_id == conv_id).count()
    if msg_count == 1:
        conv.title = body.content[:50]
        db.commit()

    # 3. 组装历史上下文(只取最近 20 条,防止 token 溢出)
    history = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.desc())
        .limit(20)
        .all()
    )
    history.reverse()
    messages_for_llm = [{"role": m.role, "content": m.content} for m in history]

    # 4. SSE 流式生成
    def generate():
        full_reply = []
        try:
            stream = llm_client.chat.completions.create(
                model=settings.DASHSCOPE_MODEL,
                messages=messages_for_llm,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                if choice.delta and choice.delta.content:
                    full_reply.append(choice.delta.content)
                    yield f"data: {json.dumps({'type': 'delta', 'content': choice.delta.content})}\n\n"

            final_content = "".join(full_reply)
            if not final_content:
                final_content = "抱歉,未能生成回复,请重试。"

            # 5. 持久化 AI 回复
            save_db = SessionLocal()
            try:
                ai_msg = Message(conversation_id=conv_id, role="assistant", content=final_content)
                save_db.add(ai_msg)
                save_db.commit()
                save_db.refresh(ai_msg)
                yield f"data: {json.dumps({'type': 'done', 'message_id': ai_msg.id, 'created_at': str(ai_msg.created_at)})}\n\n"
            finally:
                save_db.close()

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': f'AI 调用失败: {str(e)}'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")