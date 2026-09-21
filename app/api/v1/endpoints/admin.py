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


# =========================================================================
# 📬 1. MODERASI ASPIRASI PENGUNJUNG
# =========================================================================

@router.get("/wishes", response_model=List[WishResponse], summary="Daftar Semua Aspirasi")
def get_all_wishes(
    status: Optional[str] = Query(None, description="Filter status: approved, rejected, pending"),
    limit: int = Query(50, le=200, description="Batas jumlah data"),
    offset: int = Query(0, ge=0, description="Offset data"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Mengambil seluruh daftar aspirasi pengunjung dengan opsi filter status dan paginasi.
    """
    query = db.query(Wish)
    if status:
        query = query.filter(Wish.status == status)
    return query.order_by(Wish.created_at.desc()).offset(offset).limit(limit).all()


@router.patch("/wishes/{wish_id}/status", response_model=WishResponse, summary="Ubah Status Aspirasi")
def update_wish_status(
    wish_id: str,
    status: str = Query(..., description="Status baru: approved, rejected, pending"), 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Memperbarui status satu aspirasi (misalnya menyetujui atau menolak aspirasi).
    """
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Data aspirasi tidak ditemukan")
    
    if status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Status tidak valid")
        
    wish.status = status
    db.commit()
    db.refresh(wish)
    return wish


@router.post("/wishes/bulk-status", summary="Ubah Status Aspirasi Massal")
def bulk_update_status(
    payload: BulkStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Mengubah status beberapa aspirasi sekaligus secara massal.
    """
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


@router.delete("/wishes/{wish_id}", summary="Hapus Aspirasi")
def delete_wish(
    wish_id: str, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Menghapus permanen satu data aspirasi berdasarkan ID.
    """
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    db.delete(wish)
    db.commit()
    return {"message": "Aspirasi berhasil dihapus"}


@router.post("/wishes/bulk-delete", summary="Hapus Aspirasi Massal")
def bulk_delete_wishes(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Menghapus permanen banyak aspirasi sekaligus secara massal.
    """
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Daftar ID tidak boleh kosong")

    deleted_count = db.query(Wish).filter(Wish.id.in_(payload.ids)).delete(synchronize_session=False)
    db.commit()
    return {
        "message": f"{deleted_count} data aspirasi berhasil dihapus",
        "deleted_count": deleted_count
    }


# =========================================================================
# 📊 2. STATISTIK & ANALITIK
# =========================================================================

@router.get("/analytics", summary="Statistik Analitik Dashboard")
def get_analytics(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """
    Mengambil ringkasan jumlah total aspirasi, disetujui, ditolak, dan pending.
    """
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


# =========================================================================
# ⚙️ 3. PENGATURAN TAMPILAN LAYAR
# =========================================================================

@router.get("/settings", summary="Ambil Pengaturan Kuota Tampilan")
def get_settings(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """
    Mengambil batas maksimal kuota aspirasi yang akan dirender di layar Unity.
    """
    setting = db.query(AppSetting).filter(AppSetting.key == "frontend_display_limit").first()
    limit_val = int(setting.value) if setting and setting.value.isdigit() else 50
    return {
        "frontend_display_limit": limit_val
    }


@router.post("/settings", summary="Perbarui Pengaturan Kuota Tampilan")
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Menyimpan batas kuota tampilan aspirasi baru untuk layar Unity.
    """
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