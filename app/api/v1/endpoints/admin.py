from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.models.wish import Wish
from app.models.user import User
from app.models.setting import AppSetting
from app.schemas.wish import WishResponse
from app.api.v1.deps import get_current_admin

router = APIRouter()

class BulkStatusUpdate(BaseModel):
    ids: List[str]
    status: str

class BulkDeleteRequest(BaseModel):
    ids: List[str]

class SettingsUpdate(BaseModel):
    frontend_display_limit: int

@router.get("/wishes", response_model=List[WishResponse])
def get_all_wishes(
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    query = db.query(Wish)
    if status:
        query = query.filter(Wish.status == status)
    return query.order_by(Wish.created_at.desc()).offset(offset).limit(limit).all()

@router.patch("/wishes/{wish_id}/status", response_model=WishResponse)
def update_wish_status(
    wish_id: str,
    status: str, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Data aspirasi tidak ditemukan")
    
    if status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Status tidak valid")
        
    wish.status = status
    db.commit()
    db.refresh(wish)
    return wish

@router.post("/wishes/bulk-status")
def bulk_update_status(
    payload: BulkStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Daftar ID tidak boleh kosong")

    if payload.status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Status tidak valid")

    updated_count = db.query(Wish).filter(Wish.id.in_(payload.ids)).update(
        {Wish.status: payload.status}, synchronize_session=False
    )
    db.commit()
    return {
        "message": f"{updated_count} data aspirasi berhasil diubah statusnya",
        "updated_count": updated_count
    }

@router.delete("/wishes/{wish_id}")
def delete_wish(
    wish_id: str, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    db.delete(wish)
    db.commit()
    return {"message": "Aspirasi berhasil dihapus"}

@router.post("/wishes/bulk-delete")
def bulk_delete_wishes(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Daftar ID tidak boleh kosong")

    deleted_count = db.query(Wish).filter(Wish.id.in_(payload.ids)).delete(synchronize_session=False)
    db.commit()
    return {
        "message": f"{deleted_count} data aspirasi berhasil dihapus",
        "deleted_count": deleted_count
    }

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    total = db.query(func.count(Wish.id)).scalar() or 0
    approved = db.query(func.count(Wish.id)).filter(Wish.status == "approved").scalar() or 0
    rejected = db.query(func.count(Wish.id)).filter(Wish.status == "rejected").scalar() or 0
    pending = db.query(func.count(Wish.id)).filter(Wish.status == "pending").scalar() or 0
    
    return {
        "total_wishes": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    }

@router.get("/settings")
def get_settings(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    setting = db.query(AppSetting).filter(AppSetting.key == "frontend_display_limit").first()
    limit_val = int(setting.value) if setting and setting.value.isdigit() else 50
    return {
        "frontend_display_limit": limit_val
    }

@router.post("/settings")
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    if payload.frontend_display_limit <= 0:
        raise HTTPException(status_code=400, detail="Batas kuota harus lebih besar dari 0")
        
    setting = db.query(AppSetting).filter(AppSetting.key == "frontend_display_limit").first()
    if not setting:
        setting = AppSetting(key="frontend_display_limit", value=str(payload.frontend_display_limit))
        db.add(setting)
    else:
        setting.value = str(payload.frontend_display_limit)
        
    db.commit()
    db.refresh(setting)
    return {
        "message": "Pengaturan berhasil diperbarui",
        "frontend_display_limit": int(setting.value)
    }