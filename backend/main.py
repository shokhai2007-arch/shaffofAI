from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, services
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shaffof AI Backend", description="Tender Risk Analysis API")

# CORS (Barcha frontend ulanishlariga ruxsat)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    print("Dastur ishga tushmoqda, boshlang'ich ma'lumotlarni olyapmiz...")
    count = services.fetch_and_populate(db, max_records=100)
    print(f"Startup davomida API'dan jami {count} ma'lumot olindi.")

@app.get("/api/tenders", response_model=List[schemas.Tender])
def read_tenders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tenders = services.get_tenders(db, skip=skip, limit=limit)
    return tenders

@app.get("/api/tenders/{tender_id}", response_model=schemas.Tender)
def read_tender(tender_id: str, db: Session = Depends(get_db)):
    tender = services.get_tender(db, tender_id=tender_id)
    if tender is None:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender

import random

def generate_notifications_for_tender(tender: schemas.Tender) -> list:
    notifications = []
    time_str = f"{random.randint(1, 59)} daqiqa oldin"
    
    if tender.score >= 80:
        notifications.append({
            "id": f"N_{tender.id}_H",
            "type": "critical",
            "icon": "fas fa-triangle-exclamation",
            "title": "Kritik Risk Aniqlandi!",
            "desc": f"{tender.lot_id} tender qator sabablarga ko'ra jami {tender.score} xavf balliga ega.",
            "time": time_str,
            "tender": tender.id,
            "unread": True,
            "tags": [{"text": "Yuqori xavf", "class": "risk-high"}],
            "severityScore": tender.score
        })
        
    factors = tender.factors
    if not isinstance(factors, dict):
        return notifications

    if factors.get('priceAnomaly', {}).get('triggered'):
        notifications.append({
            "id": f"N_{tender.id}_PA",
            "type": "critical",
            "icon": "fas fa-money-bill-wave",
            "title": "Narx Anomaliyasi",
            "desc": factors['priceAnomaly'].get('desc', 'Tender narxi baland'),
            "time": time_str,
            "tender": tender.id,
            "unread": True,
            "tags": [{"text": "+40 ball", "class": "badge-blue"}],
            "severityScore": 95
        })

    if factors.get('newCompany', {}).get('triggered'):
        notifications.append({
            "id": f"N_{tender.id}_NC",
            "type": "warning",
            "icon": "fas fa-building",
            "title": "Yangi Kompaniya",
            "desc": factors['newCompany'].get('desc', "Yangi kompaniya g'olibga aylangan"),
            "time": time_str,
            "tender": tender.id,
            "unread": True,
            "tags": [{"text": "+30 ball", "class": "badge-blue"}],
            "severityScore": 75
        })

    if factors.get('addressMatch', {}).get('triggered'):
        notifications.append({
            "id": f"N_{tender.id}_SA",
            "type": "critical",
            "icon": "fas fa-location-dot",
            "title": "Manzil Mosligi",
            "desc": factors['addressMatch'].get('desc', 'Ishtirokchilar manzili bir xil'),
            "time": time_str,
            "tender": tender.id,
            "unread": True,
            "tags": [{"text": "+50 ball", "class": "badge-blue"}],
            "severityScore": 85
        })

    return notifications

def generate_warning_notifications(tenders: list) -> list:
    medium_count = sum(1 for t in tenders if getattr(t, 'riskLevel', '') == 'medium')
    warnings = []
    if medium_count >= 3:
        warnings.append({
            "id": f"N_WARN_MED_{random.randint(100,999)}",
            "type": "warning",
            "icon": "fas fa-circle-exclamation",
            "title": "O'rtacha Risk — Kuzatuvda",
            "desc": f"Tizimda jami {medium_count} ta tender o'rtacha risk darajasida baholandi. Ularni alohida tahlil qilish tavsiya etiladi.",
            "time": "Hozirgina",
            "tender": None,
            "unread": True,
            "tags": [{"text": "O'rtacha xavf", "class": "risk-medium"}],
            "severityScore": 60
        })
    return warnings

def generate_system_notifications(total_count: int) -> list:
    infos = []
    infos.append({
        "id": f"N_SYS_SYNC_{random.randint(100,999)}",
        "type": "info",
        "icon": "fas fa-database",
        "title": "Ma'lumotlar Bazasi Sinxronlashdi",
        "desc": f"xarid.uz bilan orqa fonda sinxronlash yakunlandi. Jami {total_count} ta tender ma'lumotlari bazadan muvaffaqiyatli o'qildi.",
        "time": "Yaqinda",
        "tender": None,
        "unread": False,
        "tags": [{"text": "Sinxronlandi", "class": "badge-green"}],
        "severityScore": 10
    })
    return infos

@app.get("/api/notifications/")
def read_notifications(db: Session = Depends(get_db)):
    tenders = services.get_tenders(db, skip=0, limit=200)
    all_notifs = []
    parsed_tenders = []
    
    for t in tenders:
        t_model = schemas.Tender.model_validate(t)
        parsed_tenders.append(t_model)
        all_notifs.extend(generate_notifications_for_tender(t_model))
        
    # Aggegated (Warning) va System (Info) triggerlari qo'shiladi
    all_notifs.extend(generate_warning_notifications(parsed_tenders))
    all_notifs.extend(generate_system_notifications(len(parsed_tenders)))
        
    # Eng baland xavflarini list boshiga o'tkazish
    all_notifs = sorted(all_notifs, key=lambda x: x.get("severityScore", 0), reverse=True)
    
    return [n for n in all_notifs][:20]
