from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from uuid import UUID


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    user_name: str = Field(nullable=False)
    password: str = Field(nullable=False)  # This will store the hashed password


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")
    # Relationship to testimonials
    testimonials: List["Testimonial"] = Relationship(back_populates="user")


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationship to user
    user: User = Relationship(back_populates="tasks")


class TestimonialBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=100)
    rating: int = Field(ge=1, le=5)
    message: str = Field(min_length=10, max_length=1000)


class Testimonial(TestimonialBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationship to user
    user: User = Relationship(back_populates="testimonials")


class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    # user_id will be taken from the path parameter, not the request body


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)


class TaskCreateInternal(TaskBase):
    user_id: uuid.UUID = Field(foreign_key="user.id")  # For internal use when creating with user_id


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: Optional[bool] = Field(default=None)
    # user_id should not be updatable through this endpoint


class TaskPublic(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID  # Include user_id in the public representation
    created_at: datetime
    updated_at: datetime


class TaskWithUser(TaskPublic):
    user: User


class TestimonialCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=100)
    rating: int = Field(ge=1, le=5)
    message: str = Field(min_length=10, max_length=1000)
    # user_id will be taken from the authentication context


class TestimonialUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    message: Optional[str] = Field(default=None, min_length=10, max_length=1000)


class TestimonialPublic(TestimonialBase):
    id: uuid.UUID
    user_id: uuid.UUID  # Include user_id in the public representation
    created_at: datetime
    updated_at: datetime


class UserRegistration(SQLModel):
    user_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=6, max_length=128)  # Plain password to be hashed


class UserPublic(SQLModel):
    id: uuid.UUID
    user_name: str
    email: str
    created_at: datetime
    updated_at: datetime


# Chat models
from enum import Enum

class MessageRole(str, Enum):
    """Message role enum."""
    USER = "user"
    ASSISTANT = "assistant"


class ConversationBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    user_id: uuid.UUID = Field(foreign_key="user.id")


class Conversation(ConversationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: str = Field(min_length=1, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class MessageBase(SQLModel):
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    role: str = Field(sa_column_kwargs={"name": "role"})  # 'user' or 'assistant'
    content: str = Field(min_length=1)


class Message(MessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    role: str = Field(sa_column_kwargs={"name": "role"})  # 'user' or 'assistant'
    content: str = Field(min_length=1)
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")

    class Config:
        arbitrary_types_allowed = True

    def dict(self, **kwargs):
        """Override dict method to ensure tool_calls is properly serialized."""
        import json
        data = super().dict(**kwargs)
        # If tool_calls is a string, parse it
        if isinstance(data.get('tool_calls'), str):
            try:
                data['tool_calls'] = json.loads(data['tool_calls'])
            except (json.JSONDecodeError, TypeError):
                data['tool_calls'] = None
        return data


class ConversationCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    user_id: uuid.UUID


class ConversationUpdate(SQLModel):
    """Schema for updating an existing conversation."""
    title: Optional[str] = None


class ConversationPublic(ConversationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MessageCreate(SQLModel):
    conversation_id: Optional[uuid.UUID] = None
    role: str = Field(regex="^(user|assistant)$")  # Only allow 'user' or 'assistant'
    content: str = Field(min_length=1)
    tool_calls: Optional[List[Dict[str, Any]]] = None


from pydantic import field_validator

class MessagePublic(MessageBase):
    id: uuid.UUID
    created_at: datetime
    tool_calls: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @field_validator('tool_calls', mode='before')
    @classmethod
    def parse_tool_calls(cls, v):
        """Parse tool_calls if it's a JSON string."""
        if v is None:
            return None
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v