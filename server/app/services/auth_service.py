from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.security.hashing import verify_password, get_password_hash
from app.security.jwt import create_access_token
from app.services.anomaly_service import AnomalyService

class AuthService:
    @staticmethod
    def register(
        db: Session,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.STUDENT,
        student_id: Optional[str] = None
    ) -> User:
        user_repo = UserRepository(db)
        
        # Check email uniqueness
        existing_email = user_repo.get_by_email(email)
        if existing_email:
            raise ValueError("Email already registered")

        # Check student_id uniqueness if student
        if role == UserRole.STUDENT and student_id:
            existing_sid = user_repo.get_by_student_id(student_id)
            if existing_sid:
                raise ValueError("Student ID already in use")

        hashed = get_password_hash(password)
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed,
            full_name=full_name.strip(),
            role=role,
            student_id=student_id.strip() if student_id else None,
            is_active=True
        )
        created = user_repo.create(user)

        AnomalyService.log_suspicious_activity(
            db=db,
            event_type="USER_REGISTERED",
            user_id=created.id,
            details={"email": email, "role": role.value},
            severity="INFO"
        )
        return created

    @staticmethod
    def authenticate(
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_token(user: User) -> Dict[str, Any]:
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name,
            "student_id": user.student_id
        }
        token = create_access_token(data=token_data)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "student_id": user.student_id
            }
        }
