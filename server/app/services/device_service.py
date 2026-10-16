from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.device_request import DeviceRequest, DeviceRequestStatus
from app.models.user import User
from app.repositories.device_repo import DeviceRepository, DeviceRequestRepository
from app.services.anomaly_service import AnomalyService

def utcnow():
    return datetime.now(timezone.utc)

class DeviceService:
    @staticmethod
    def register_device(
        db: Session,
        user: User,
        device_uuid: str,
        device_name: str
    ) -> Device:
        device_repo = DeviceRepository(db)
        existing = device_repo.get_by_user_id(user.id)
        if existing:
            raise ValueError(
                f"User is already bound to device {existing.device_name} ({existing.device_uuid}). "
                "Changing devices requires an Organizer Approval Request."
            )

        # Check if UUID is already bound to another student
        uuid_owner = device_repo.get_by_uuid(device_uuid)
        if uuid_owner and uuid_owner.user_id != user.id:
            AnomalyService.log_suspicious_activity(
                db=db,
                event_type="DEVICE_MULTI_STUDENT_COLLISION",
                user_id=user.id,
                details={"colliding_user_id": uuid_owner.user_id, "device_uuid": device_uuid},
                severity="CRITICAL"
            )
            raise ValueError("This physical device is already bound to another student account.")

        device = Device(
            user_id=user.id,
            device_uuid=device_uuid.strip(),
            device_name=device_name.strip(),
            is_active=True
        )
        created = device_repo.create(device)
        
        AnomalyService.log_suspicious_activity(
            db=db,
            event_type="DEVICE_REGISTERED",
            user_id=user.id,
            details={"device_uuid": device_uuid, "device_name": device_name},
            severity="INFO"
        )
        return created

    @staticmethod
    def create_change_request(
        db: Session,
        user: User,
        new_device_uuid: str,
        new_device_name: str,
        reason: str
    ) -> DeviceRequest:
        device_repo = DeviceRepository(db)
        req_repo = DeviceRequestRepository(db)
        
        current_device = device_repo.get_by_user_id(user.id)
        old_uuid = current_device.device_uuid if current_device else "NONE"

        request = DeviceRequest(
            user_id=user.id,
            old_device_uuid=old_uuid,
            new_device_uuid=new_device_uuid.strip(),
            new_device_name=new_device_name.strip(),
            reason=reason.strip(),
            status=DeviceRequestStatus.PENDING
        )
        created = req_repo.create(request)
        
        AnomalyService.log_suspicious_activity(
            db=db,
            event_type="DEVICE_CHANGE_REQUESTED",
            user_id=user.id,
            details={"old_uuid": old_uuid, "new_uuid": new_device_uuid, "reason": reason},
            severity="WARNING"
        )
        return created

    @staticmethod
    def review_change_request(
        db: Session,
        request_id: int,
        reviewer_id: int,
        approve: bool
    ) -> DeviceRequest:
        req_repo = DeviceRequestRepository(db)
        device_repo = DeviceRepository(db)

        req = req_repo.get_by_id(request_id)
        if not req:
            raise ValueError("Change request not found")
        if req.status != DeviceRequestStatus.PENDING:
            raise ValueError("Request has already been processed")

        req.reviewed_by = reviewer_id
        req.reviewed_at = utcnow()

        if approve:
            req.status = DeviceRequestStatus.APPROVED
            # Deactivate old device
            old_device = device_repo.get_by_user_id(req.user_id)
            if old_device:
                old_device.is_active = False
                device_repo.update(old_device)

            # Check if new device record exists or create new
            new_device = Device(
                user_id=req.user_id,
                device_uuid=req.new_device_uuid,
                device_name=req.new_device_name,
                is_active=True
            )
            device_repo.create(new_device)

            AnomalyService.log_suspicious_activity(
                db=db,
                event_type="DEVICE_CHANGE_APPROVED",
                user_id=req.user_id,
                details={"request_id": req.id, "new_uuid": req.new_device_uuid, "reviewer": reviewer_id},
                severity="INFO"
            )
        else:
            req.status = DeviceRequestStatus.REJECTED
            AnomalyService.log_suspicious_activity(
                db=db,
                event_type="DEVICE_CHANGE_REJECTED",
                user_id=req.user_id,
                details={"request_id": req.id, "reviewer": reviewer_id},
                severity="INFO"
            )

        req_repo.update(req)
        return req
