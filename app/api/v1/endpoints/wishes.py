from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.wish import Wish
from app.models.setting import AppSetting
from app.schemas.wish import WishCreate, WishResponse
from app.core.profanity import contains_profanity

router = APIRouter()


@router.post("", response_model=WishResponse, summary="Kirim Aspirasi Pengunjung")
@router.post("/", response_model=WishResponse, include_in_schema=False)
def submit_wish(
    payload: WishCreate, 
    db: Session = Depends(get_db)
):
    """
    Menerima input aspirasi/harapan dari pengunjung di layar Unity Dream Wall.
    Melakukan sanitasi dan penyaringan kata-kata tidak pantas (*profanity filter*).
    """
    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Teks aspirasi tidak boleh kosong")

    name = payload.name.strip() if payload.name else None
    age_range = payload.age_range.strip() if payload.age_range else None

    # Saring kata kasar / tidak pantas
    is_profane, detected_words = contains_profanity(clean_text)
    if not is_profane and name:
        is_profane, detected_words = contains_profanity(name)

    if is_profane:
        # Tetap disimpan ke database dengan status 'rejected' untuk audit/log
        rejected_wish = Wish(
            name=name,
            age_range=age_range,
            text=clean_text,
            status="rejected"
        )
        db.add(rejected_wish)
        db.commit()
        db.refresh(rejected_wish)

        # Kembalikan HTTP Status 422 agar aplikasi frontend/Unity memberi tahu user untuk input ulang
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Aspirasi terdeteksi mengandung kata yang tidak pantas. Silakan gunakan bahasa yang sopan.",
                "status": "rejected",
                "id": rejected_wish.id
            }
        )

    # Jika bersih, simpan dengan status 'approved' dan kembalikan HTTP Status 200
    new_wish = Wish(
        name=name,
        age_range=age_range,
        text=clean_text,
        status="approved"
    )
    db.add(new_wish)
    db.commit()
    db.refresh(new_wish)
    
    return new_wish


@router.get("/approved", response_model=List[WishResponse], summary="Ambil Aspirasi yang Disetujui (Tampilan Layar)")
def get_approved_wishes(
    db: Session = Depends(get_db)
):
    """
    Mengambil daftar aspirasi berstatus 'approved' untuk dirender di layar utama Unity.
    Batas kuota jumlah aspirasi mengikuti konfigurasi pengaturan dari CMS.
    """
    # Batas kuota tampilan murni diambil dari database setting CMS
    setting = db.query(AppSetting).filter(AppSetting.key == "frontend_display_limit").first()
    limit = int(setting.value) if setting and setting.value.isdigit() else 50

    wishes = db.query(Wish).filter(Wish.status == "approved").order_by(Wish.created_at.desc()).limit(limit).all()
    return wishes