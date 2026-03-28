import requests
import random
import json
from datetime import datetime
from .models import Tender, Participant
from .serializers import TenderSerializer

API_CONFIGS = [
    {
        "url": "https://xarid-api-auction.uzex.uz/Common/GetCompletedDeals",
        "payload": {"region_ids": [], "from": 1, "to": 30},
        "validation": "N8kOSBDXFtCCwQRrlDaQmc2ucsmaDMYf2inhbelvSPo+14zBqsIwywfyPq7u5VC1cLcuSQ0lepNs1nDFykWUK3p80kF9YiL1VW0WREMLHqD2oQdt1tntR+hpu2Vv5dpM0ZlK6iFdeC83Gp9uhLSpWIdbp3vHmmMk19lXAExG0zM="
    },
    {
        "url": "https://xarid-api-shop.uzex.uz/Common/GetCompletedDeals",
        "payload": {"region_ids": [], "display_on_shop": 1, "display_on_national": 0, "year_id": 2026, "from": 1, "to": 30},
        "validation": "d54I2vuukacprnFzT5sVy8p68vRAPjG/pbMf0WPEhvJwtNTFPnZ6LoO7zyaX+ql73iSxRs+NZtoAnx/w/7RvaUgYG9e/OqE7rNv/hgObfW23ergUJ582Czk8V7OtLcCYbf1KCKR2XXiJH3QrAoR9BYUmQa+d4Uy1JAdFBallLII="
    },
    {
        "url": "https://xarid-api-shop.uzex.uz/Common/GetCompletedDeals",
        "payload": {"region_ids": [], "display_on_shop": 0, "display_on_national": 1, "year_id": 2026, "from": 1, "to": 30},
        "validation": "AIgaHNWPAmTvqfrEqDd1zh541qvQcL82T+RT1WiMfUqjyQNT0Hgsi72hIR76QP1IHo15Fi3UNsOIM2J+E3K8sKWu+mGOuK1l28IUF4e/nKA2fMoUP1XLRJjtg0dsxTerkVJCBJdf+cMvr/5x00fsGD3JD2qTHqe040iroUFBfCw="
    }
]

HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9,uz;q=0.8,ru;q=0.7',
    'Origin': 'https://xarid.uzex.uz',
    'Referer': 'https://xarid.uzex.uz/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'Cookie': '_ym_uid=1774625614260171448; _ym_d=1774625614; _ym_isad=2',
    'Content-Type': 'application/json; charset=UTF-8'
}

def generate_mock_fields(amount: float):
    marketAvg = amount / random.uniform(1.2, 2.5) if amount > 0 else 1000000
    companyAgeMonths = random.choices(
        population=range(6, 37),
        weights=[1 if x < 12 else 5 for x in range(6, 37)]
    )[0]
    sameAddress = random.random() < 0.15
    
    score = 0
    factors_dict = {
        "priceAnomaly": {"triggered": False, "points": 0, "desc": "Bozor narxiga mos"},
        "newCompany": {"triggered": False, "points": 0, "desc": "Kompaniya yetarlicha eski"},
        "addressMatch": {"triggered": False, "points": 0, "desc": "Manzillar turlicha"}
    }
    
    if companyAgeMonths < 6:
        score += 30
        factors_dict["newCompany"] = {"triggered": True, "points": 30, "desc": f"Kompaniya {companyAgeMonths} oy oldin tashkil etilgan (6 oydan kam)"}
    if sameAddress:
        score += 50
        factors_dict["addressMatch"] = {"triggered": True, "points": 50, "desc": "Ishtirokchilardan kamida ikkitasi bir xil yuridik manzilda ro'yxatdan o'tgan"}
        
    if amount > (marketAvg * 2):
        score += 40
        factors_dict["priceAnomaly"] = {"triggered": True, "points": 40, "desc": f"Tender summasi bozor o'rtachasidan {(amount/marketAvg):.1f}x yuqori"}

    if score >= 80:
        r_level, r_label, r_color = "high", "Yuqori Xavf", "#f44336"
    elif score >= 40:
        r_level, r_label, r_color = "medium", "O'rtacha Xavf", "#ff7043"
    else:
        r_level, r_label, r_color = "low", "Past Xavf", "#4caf50"
        
    return {
        "marketAvg": marketAvg,
        "companyAgeMonths": companyAgeMonths,
        "sameAddress": sameAddress,
        "score": score,
        "riskLevel": r_level,
        "riskLabel": r_label,
        "riskColor": r_color,
        "factors": factors_dict # Django JSONField takes dict
    }

def generate_fake_participants():
    fake_companies = ["MCHJ 'PROGRESS IDEAL'", "'MEGA BUILD' Xususiy", "'INNOTECH' MCHJ", "'SMART SYSTEMS' MCHJ"]
    count = random.randint(2, 4)
    participants = []
    fake_directors = ["Eshmatov Toshmat", "Aliyev Vali", "G'aniyev Eson", "Tursunov Akbar"]
    fake_addresses = ["Toshkent, Yunusobod", "Farg'ona, Quva", "Samarqand, Narpay", "Buxoro, Qorako'l"]
    
    for comp in random.sample(fake_companies, count - 1):
        participants.append({
            "name": comp, 
            "inn": str(random.randint(200000000, 399999999)), 
            "role": "Ishtirokchi",
            "director": random.choice(fake_directors),
            "address": random.choice(fake_addresses),
            "type": "company",
            "ageMonths": random.randint(6, 40)
        })
    return participants

def parse_date(date_str: str):
    try:
        if date_str:
            return datetime.fromisoformat(date_str).date()
    except:
        pass
    return datetime.now().date()

def generate_notifications_for_tender(tender_data: dict) -> list:
    notifications = []
    time_str = f"{random.randint(1, 59)} daqiqa oldin"
    score = tender_data.get('score', 0)
    t_id = tender_data.get('lot_id', 'unknown')
    
    if score >= 80:
        notifications.append({
            "id": f"N_{t_id}_H",
            "type": "critical",
            "icon": "fas fa-triangle-exclamation",
            "title": "Kritik Risk Aniqlandi!",
            "desc": f"{t_id} tender qator sabablarga ko'ra jami {score} xavf balliga ega.",
            "time": time_str,
            "tender": t_id,
            "unread": True,
            "tags": [{"text": "Yuqori xavf", "class": "risk-high"}],
            "severityScore": score
        })
        
    factors = tender_data.get('factors', {})
    if not isinstance(factors, dict):
        return notifications

    if factors.get('priceAnomaly', {}).get('triggered'):
        notifications.append({
            "id": f"N_{t_id}_PA",
            "type": "critical",
            "icon": "fas fa-money-bill-wave",
            "title": "Narx Anomaliyasi",
            "desc": factors['priceAnomaly'].get('desc', 'Tender narxi baland'),
            "time": time_str,
            "tender": t_id,
            "unread": True,
            "tags": [{"text": "+40 ball", "class": "badge-blue"}],
            "severityScore": 95
        })

    if factors.get('newCompany', {}).get('triggered'):
        notifications.append({
            "id": f"N_{t_id}_NC",
            "type": "warning",
            "icon": "fas fa-building",
            "title": "Yangi Kompaniya",
            "desc": factors['newCompany'].get('desc', "Yangi kompaniya g'olibga aylangan"),
            "time": time_str,
            "tender": t_id,
            "unread": True,
            "tags": [{"text": "+30 ball", "class": "badge-blue"}],
            "severityScore": 75
        })

    if factors.get('addressMatch', {}).get('triggered'):
        notifications.append({
            "id": f"N_{t_id}_SA",
            "type": "critical",
            "icon": "fas fa-location-dot",
            "title": "Manzil Mosligi",
            "desc": factors['addressMatch'].get('desc', 'Ishtirokchilar manzili bir xil'),
            "time": time_str,
            "tender": t_id,
            "unread": True,
            "tags": [{"text": "+50 ball", "class": "badge-blue"}],
            "severityScore": 85
        })

    return notifications

def generate_warning_notifications(tenders_data: list) -> list:
    medium_count = sum(1 for t in tenders_data if t.get('riskLevel') == 'medium')
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
    return [{
        "id": f"N_SYS_SYNC_{random.randint(100,999)}",
        "type": "info",
        "icon": "fas fa-database",
        "title": "Ma'lumotlar Bazasi Sinxronlashdi",
        "desc": f"xarid.uz bilan orqa fonda sinxronlash yakunlandi. Jami {total_count} ta tender ma'lumotlari mavjud.",
        "time": "Yaqinda",
        "tender": None,
        "unread": False,
        "tags": [{"text": "Sinxronlandi", "class": "badge-green"}],
        "severityScore": 10
    }]
