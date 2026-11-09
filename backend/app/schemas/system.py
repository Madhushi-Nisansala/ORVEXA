from typing import Literal

from pydantic import BaseModel

class RootResponse(BaseModel):
    application: str
    version: str
    status: Literal['operational']
    api_prefix: str

class HealthResponse(BaseModel):
    status: Literal['healthy', 'degraded']
    application: str
    version: str
    database: Literal['connected', 'unavailable']

class ReadinessResponse(BaseModel):
    status: Literal['ready', 'not_ready']
    checks: dict[str, str]
