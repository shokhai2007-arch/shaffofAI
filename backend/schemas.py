from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from typing import List, Optional, Any
import datetime as dt
import json

class ParticipantBase(BaseModel):
    name: str
    role: str
    type: str = "company"
    director: Optional[str] = None
    address: Optional[str] = None
    ageMonths: Optional[int] = None

class ParticipantCreate(ParticipantBase):
    pass

class Participant(ParticipantBase):
    model_config = ConfigDict(from_attributes=True)

class TenderBase(BaseModel):
    lot_id: str
    name: Optional[str] = None
    org: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None
    date: Optional[dt.date] = None
    amount: float
    marketAvg: Optional[float] = None
    companyAgeMonths: Optional[int] = None
    sameAddress: bool = False
    score: int = 0
    riskLevel: str = "low"
    riskLabel: str = "Xavfsiz"
    riskColor: str = "#4caf50"

    @field_validator('date', mode='before')
    def parse_date(cls, v):
        if hasattr(v, 'date'):
            return v.date()
        return v

class TenderCreate(TenderBase):
    participants: List[ParticipantCreate] = []

class Tender(TenderBase):
    participants: List[Participant] = []
    factors: Any = None

    @computed_field
    def id(self) -> str:
        return self.lot_id

    @field_validator('factors', mode='before')
    def parse_factors(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        return v or {}

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
