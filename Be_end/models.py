from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, JSON, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="新对话")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    graph_json = Column(JSON, default={})
    status = Column(String(20), default="draft")  # draft | published
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="workflows")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(SAEnum("user", "assistant", "system", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    doc_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    chunk_count = Column(Integer, default=0)
    status = Column(SAEnum("processing", "ready", "failed", name="document_status"), default="ready")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    knowledge_base = relationship("KnowledgeBase", back_populates="documents")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="running")  # running | success | failed
    input_json = Column(JSON, default={})
    output_json = Column(JSON, default={})
    logs_json = Column(JSON, default=[])
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", backref="runs")
    user = relationship("User", backref="workflow_runs")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    category = Column(String(50), default="general")
    schema_json = Column(JSON, default={})
    handler_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelProfile(Base):
    __tablename__ = "model_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # qianwen | deepseek | gpt | claude | custom
    base_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=False)
    model_id = Column(String(100), nullable=False)
    config_json = Column(JSON, default={})
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="model_profiles")