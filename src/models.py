from typing import Literal
from pydantic import BaseModel, Field

class HumanHealthRequest(BaseModel):
    age: int = Field(ge=0)
    weight: float = Field(ge=0)
    height: float = Field(ge=0)
    gender: Literal["male", "female"] 
    symptoms: list[str] = Field(default_factory=list)
    temperatureF: float = Field(ge=0)
    