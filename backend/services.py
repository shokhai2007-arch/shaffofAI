import requests
import random
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas
import json

# 3 xil URL'lar va Ularning Payloadlari (open_urls.txt)
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
    # marketAvg: amount / random(1.2 - 2.5)
    marketAvg = amount / random.uniform(1.2, 2.5)
    
    # companyAgeMonths: random 6-36
    companyAgeMonths = random.choices(
        population=range(6, 37),
        weights=[1 if x < 12 else 5 for x in range(6, 37)] # Yangilar kamroq tushadi (Risk balanslash)
    )[0]
    
    # sameAddress: 10-20% true
    sameAddress = random.random() < 0.15
    
    # Risk Hisoblash
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

    # Risk Levels
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
        "factors": json.dumps(factors_dict)
    }

def generate_fake_participants():
    fake_companies = ["MCHJ 'PROGRESS IDEAL'", "'MEGA BUILD' Xususiy", "'INNOTECH' MCHJ", "'SMART SYSTEMS' MCHJ"]
    count = random.randint(2, 4)
    participants = []
    fake_directors = ["Eshmatov Toshmat", "Aliyev Vali", "G'aniyev Eson", "Tursunov Akbar"]
    fake_addresses = ["Toshkent, Yunusobod", "Farg'ona, Quva", "Samarqand, Narpay", "Buxoro, Qorako'l"]
    
    for comp in random.sample(fake_companies, count - 1): # Biri g'olib qo'shiladi keyin
        inn = str(random.randint(200000000, 399999999))
        participants.append({
            "name": comp, 
            "inn": inn, 
            "role": "Ishtirokchi",
            "director": random.choice(fake_directors),
            "address": random.choice(fake_addresses),
            "type": "company",
            "ageMonths": random.randint(6, 40)
        })
    return participants

def parse_date(date_str: str) -> datetime:
    try:
        if date_str:
            return datetime.fromisoformat(date_str)
    except:
        pass
    return datetime.now()

def fetch_and_populate(db: Session, max_records: int = 100):
    total_fetched = 0

    for config in API_CONFIGS:
        if total_fetched >= max_records:
            break
            
        try:
            req_headers = HEADERS.copy()
            if "validation" in config:
                req_headers["Validation"] = config["validation"]
                
            res = requests.post(config["url"], headers=req_headers, json=config["payload"], timeout=15)
            if res.status_code == 200:
                data = res.json()
                items = []
                if isinstance(data, list):
                    items = data
                elif 'data' in data:
                    items = data['data']
                elif 'items' in data:
                    items = data['items']

                for item in items:
                    if total_fetched >= max_records:
                        break
                        
                    t_id = str(item.get("lot_display_no") or item.get("lot_id"))
                    
                    # Baza mavjudligini tekshirish
                    existing = db.query(models.Tender).filter(models.Tender.lot_id == t_id).first()
                    if existing:
                        continue
                        
                    # Oddiy Fieldlar
                    t_name = item.get("product_name") or item.get("category_name", "")
                    t_org = item.get("customer_name", "")
                    t_region = item.get("customer_region_name") or item.get("customer_region", "")
                    t_sector = item.get("category_name", "")
                    t_date = parse_date(item.get("deal_date", ""))
                    t_amount = float(item.get("deal_cost", 0))

                    # Generatsiya
                    mock_data = generate_mock_fields(t_amount)

                    db_tender = models.Tender(
                        lot_id=t_id,
                        name=t_name,
                        org=t_org,
                        region=t_region,
                        sector=t_sector,
                        date=t_date,
                        amount=t_amount,
                        **mock_data
                    )
                    
                    # G'olib (Real)
                    prov_name = item.get("provider_name", "Noma'lum provayder")
                    prov_inn = str(item.get("provider_inn", ""))
                    db_winner = models.Participant(
                        name=prov_name,
                        inn=prov_inn,
                        role="G'olib",
                        type="company",
                        director="Real Director (Mock)", # Hozircha random mock format
                        address="Real Address (Mock)",
                        ageMonths=mock_data["companyAgeMonths"]
                    )
                    db_tender.participants.append(db_winner)
                    
                    # Qolgan sun'iy qatnashchilar
                    for fake_p in generate_fake_participants():
                        db_p = models.Participant(
                            name=fake_p["name"],
                            inn=fake_p["inn"],
                            role=fake_p["role"],
                            type=fake_p["type"],
                            director=fake_p["director"],
                            address=fake_p["address"],
                            ageMonths=fake_p["ageMonths"]
                        )
                        db_tender.participants.append(db_p)
                    
                    db.add(db_tender)
                        
                    total_fetched += 1
            
        except Exception as e:
            print(f"Xatolik API da {config['url']}: {e}")
            pass

    db.commit()
    return total_fetched

def get_tenders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tender).offset(skip).limit(limit).all()

def get_tender(db: Session, tender_id: str):
    return db.query(models.Tender).filter(models.Tender.id == tender_id).first()
