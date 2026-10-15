from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower().strip()).first()

    def get_by_student_id(self, student_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.student_id == student_id.strip()).first()

    def get_students(self) -> List[User]:
        return self.db.query(User).filter(User.role == "STUDENT").all()
