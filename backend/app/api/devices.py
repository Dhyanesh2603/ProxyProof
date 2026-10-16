from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.device_request import DeviceRequest, DeviceRequestStatus
from app.api.deps import get_current_user, get_current_student, get_current_organizer
from app.services.device_service import DeviceService
from app.repositories.device_repo import DeviceRepository, DeviceRequestRepository

router = APIRouter(prefix="/devices", tags=["Devices"])

class RegisterDeviceRequest(BaseModel):
    device_uuid: str
    device_name: str

class DeviceChangeRequestBody(BaseModel):
    new_device_uuid: str
    new_device_name: str
    reason: str

class ReviewDeviceRequest(BaseModel):
    approve: bool

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_device(
    req: RegisterDeviceRequest,
    db: Session = Depends(get_db),
    student: User = Depends(get_current_student)
):
    try:
        device = DeviceService.register_device(
            db=db,
            user=student,
            device_uuid=req.device_uuid,
            device_name=req.device_name
        )
        return {
            "id": device.id,
            "device_uuid": device.device_uuid,
            "device_name": device.device_name,
            "registered_at": device.registered_at.isoformat() if device.registered_at else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-device")
def get_my_device(
    db: Session = Depends(get_db),
    student: User = Depends(get_current_student)
):
    repo = DeviceRepository(db)
    dev = repo.get_by_user_id(student.id)
    if not dev:
        return {"registered": False, "device": None}
    return {
        "registered": True,
        "device": {
            "id": dev.id,
            "device_uuid": dev.device_uuid,
            "device_name": dev.device_name,
            "is_active": dev.is_active,
            "registered_at": dev.registered_at.isoformat() if dev.registered_at else None,
            "last_used_at": dev.last_used_at.isoformat() if dev.last_used_at else None
        }
    }

@router.post("/change-request", status_code=status.HTTP_201_CREATED)
def request_device_change(
    req: DeviceChangeRequestBody,
    db: Session = Depends(get_db),
    student: User = Depends(get_current_student)
):
    request = DeviceService.create_change_request(
        db=db,
        user=student,
        new_device_uuid=req.new_device_uuid,
        new_device_name=req.new_device_name,
        reason=req.reason
    )
    return {
        "id": request.id,
        "status": request.status.value,
        "new_device_uuid": request.new_device_uuid,
        "new_device_name": request.new_device_name,
        "created_at": request.created_at.isoformat() if request.created_at else None
    }

@router.get("/requests")
def list_device_requests(
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    requests = db.query(DeviceRequest).order_by(DeviceRequest.created_at.desc()).all()
    out = []
    for r in requests:
        out.append({
            "id": r.id,
            "user_id": r.user_id,
            "student_name": r.user.full_name if r.user else "Unknown",
            "student_code": r.user.student_id if r.user else "N/A",
            "old_device_uuid": r.old_device_uuid,
            "new_device_uuid": r.new_device_uuid,
            "new_device_name": r.new_device_name,
            "reason": r.reason,
            "status": r.status.value,
            "reviewed_by": r.reviewed_by,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return out

@router.put("/approve/{request_id}")
def approve_or_reject_device(
    request_id: int,
    req: ReviewDeviceRequest,
    db: Session = Depends(get_db),
    organizer: User = Depends(get_current_organizer)
):
    try:
        updated = DeviceService.review_change_request(
            db=db,
            request_id=request_id,
            reviewer_id=organizer.id,
            approve=req.approve
        )
        return {
            "id": updated.id,
            "status": updated.status.value,
            "reviewed_at": updated.reviewed_at.isoformat() if updated.reviewed_at else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
