from fastapi import APIRouter, HTTPException, status

from database import (
    AuthSchema,
    create_access_token,
    create_user,
    get_user_by_email,
    verify_password,
)

router = APIRouter(tags=["auth"])


@router.post("/signup")
def signup(payload: AuthSchema):
    if get_user_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    if not payload.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name is required to sign up.",
        )

    create_user(payload.name, payload.email, payload.password)
    return {"message": "Account created successfully."}


@router.post("/login")
def login(payload: AuthSchema):
    user = get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "email": user["email"], "token_type": "bearer"}