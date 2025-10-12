from pydantic import BaseModel


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthTokenData(BaseModel):
    user_id: int | None = None

    def get_id(self) -> int | None:
        if self.user_id:
            return int(self.user_id)
        return None
