from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ── Auth ──────────────────────────────────────────────
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


# ── Chat ──────────────────────────────────────────────
class ConversationCreate(BaseModel):
    title: str = "新对话"


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    id: int
    title: str
    messages: List[MessageResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Workflow ──────────────────────────────────────────
class WorkflowCreate(BaseModel):
    name: str
    description: str = ""


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graph_json: Optional[Any] = None
    status: Optional[str] = None


class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str
    graph_json: Any
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Knowledge Base ────────────────────────────────────
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str = ""


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: str
    docCount: int = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_orm_model(cls, kb):
        return cls(
            id=kb.id,
            name=kb.name,
            description=kb.description or "",
            docCount=kb.doc_count or 0,
            createdAt=kb.created_at,
        )


class DocumentResponse(BaseModel):
    id: int
    filename: str
    chunkCount: int = 0
    status: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_orm_model(cls, doc):
        return cls(
            id=doc.id,
            filename=doc.filename,
            chunkCount=doc.chunk_count or 0,
            status=doc.status,
            createdAt=doc.created_at,
        )


# ── Tool ────────────────────────────────────────────
class ToolResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    schema: Any = {}

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, tool):
        return cls(
            id=tool.id,
            name=tool.name,
            description=tool.description or "",
            category=tool.category or "general",
            schema=tool.schema_json or {},
        )


class ToolTestRequest(BaseModel):
    params: dict = {}


class ToolCreate(BaseModel):
    name: str
    description: str = ""
    category: str = "custom"
    handler_name: str
    schema_json: Optional[Any] = None


# ── Workflow Execution ──────────────────────────────
class WorkflowRunRequest(BaseModel):
    input: Any = {}
    graph_json: Optional[Any] = None


class WorkflowRunSummary(BaseModel):
    id: int
    workflow_id: int
    status: str
    input_json: Any
    output_json: Any
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowRunDetail(WorkflowRunSummary):
    logs_json: Any = []


# ── Model Profile ─────────────────────────────────────
DEFAULT_MODEL_CONFIG = {
    "context": {
        "maxContextTokens": 8192,
        "systemTokenRatio": 10,
        "userTokenRatio": 60,
        "toolTokenRatio": 10,
        "ragTokenRatio": 20,
        "compressionStrategy": "none",
    },
    "history": {
        "strategy": "sliding_window",
        "maxMessages": 20,
        "windowSize": 10,
    },
    "agent": {
        "mode": "tool_calling",
        "toolWhitelist": [],
        "maxIterations": 10,
    },
    "observability": {
        "enableTracing": True,
        "logToolCalls": True,
    },
}


class ModelProfileCreate(BaseModel):
    name: str
    provider: str
    base_url: str
    api_key: str
    model_id: str
    config_json: Optional[Any] = None
    is_default: bool = False


class ModelProfileUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_id: Optional[str] = None
    config_json: Optional[Any] = None
    is_default: Optional[bool] = None


class ModelProfileResponse(BaseModel):
    id: int
    name: str
    provider: str
    baseUrl: str
    apiKeyMasked: str
    modelId: str
    config: Any
    isDefault: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_orm_model(cls, profile, mask_key: bool = True):
        key = profile.api_key or ""
        masked = ""
        if key:
            if len(key) <= 8:
                masked = "***"
            else:
                masked = key[:4] + "***" + key[-4:]
        return cls(
            id=profile.id,
            name=profile.name,
            provider=profile.provider,
            baseUrl=profile.base_url,
            apiKeyMasked=masked if mask_key else key,
            modelId=profile.model_id,
            config=profile.config_json or DEFAULT_MODEL_CONFIG,
            isDefault=bool(profile.is_default),
            createdAt=profile.created_at,
            updatedAt=profile.updated_at,
        )


class ModelProfileDetail(ModelProfileResponse):
    apiKey: str

    @classmethod
    def from_orm_model(cls, profile):
        base = ModelProfileResponse.from_orm_model(profile, mask_key=False)
        return cls(
            **base.model_dump(),
            apiKey=profile.api_key or "",
        )


class ModelTestRequest(BaseModel):
    message: str = "你好，请回复 OK"