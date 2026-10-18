from pydantic import BaseModel, Field
class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    owner_id: str = Field(min_length=1, max_length=100)
class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    details: str = Field(default="", max_length=5000)
    owner_id: str = Field(min_length=1, max_length=100)
class NoteIn(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    owner_id: str = Field(min_length=1, max_length=100)
class ApprovalDecision(BaseModel):
    owner_id: str
    approve: bool
