from pydantic import BaseModel


class ValidationRequest(BaseModel):
    batch: str | None = None
    host_generator_key: str | None = None