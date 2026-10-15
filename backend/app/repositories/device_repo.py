from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.device_request import DeviceRequest, DeviceRequestStatus
from app.repositories.base import BaseRepository

class DeviceRepository(BaseRepository[Device]):
    def __init__(self, db: Session):
        super().__init__(Device, db)

    def get_by_user_id(self, user_id: int) -> Optional[Device]:
        return self.db.query(Device).filter(Device.user_id == user_id, Device.is_active == True).first()

    def get_by_uuid(self, uuid: str) -> Optional[Device]:
        return self.db.query(Device).filter(Device.device_uuid == uuid.strip()).first()

    def get_active_by_user_and_uuid(self, user_id: int, uuid: str) -> Optional[Device]:
        return self.db.query(Device).filter(
            Device.user_id == user_id,
            Device.device_uuid == uuid.strip(),
            Device.is_active == True
        ).first()

class DeviceRequestRepository(BaseRepository[DeviceRequest]):
    def __init__(self, db: Session):
        super().__init__(DeviceRequest, db)

    def get_pending_requests(self) -> List[DeviceRequest]:
        return self.db.query(DeviceRequest).filter(DeviceRequest.status == DeviceRequestStatus.PENDING).all()

    def get_by_user_id(self, user_id: int) -> List[DeviceRequest]:
        return self.db.query(DeviceRequest).filter(DeviceRequest.user_id == user_id).order_by(DeviceRequest.created_at.desc()).all()
