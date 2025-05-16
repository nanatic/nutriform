from typing import Optional, Dict, Any

from pydantic import BaseModel, EmailStr


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    position: Optional[str] = None
    password: Optional[str] = None  # если будете менять пароль


class ProfileChangeRequestCreate(BaseModel):
    requested_fields: Dict[str, Any]
