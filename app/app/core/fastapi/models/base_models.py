from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime as dt
from pytz import timezone as tz

# REQUEST MODELS
class NoteSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=50) #additional validation for the inputs 
    description: str = Field(...,min_length=3, max_length=50)
    completed: str = "False"
    created_date: str = dt.now(tz("Europe/Athens")).strftime("%Y-%m-%d %H:%M")
    # abstract_json_payload: Optional[Dict]

class NoteDB(NoteSchema):
    id: int 

# RESPONSE MODELS
class SampleResponse(BaseModel):
    status: str

class HealthResponse(BaseModel):
    status: str