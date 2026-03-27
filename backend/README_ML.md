# Shaffof AI - Machine Learning va Kelajak Maqsadlari Roadmapi

Fayl: **Machine Learning (Real Data) Integratsiyasiga O'tish Rejasi**

Joriy MVP (Minimal ishchi mahsulot) holatida **Risk** darajasini hisoblash algoritmi *sun'iy yaratilgan* (`mocked`) va tasodifiy (randomized) datchiklar yordamida shakllantirilgan. Tizim qanday ishlashini baholash uchun quyidagi maydonlar sun'iy generatsiya bo'lmoqda:
- `marketAvg`
- `companyAgeMonths`
- `sameAddress`

Ushbu hujjat ularni *haqiqiy dataga (Real Data)* va *AI Modellar* integratsiyasiga qanday o'tkazish logikasini tushuntiradi.

## 1. Real Ma'lumotlar Qamrovi (Data Integrity)
- **`companyAgeMonths` (Kompaniya Yoshi):** O'zbekiston Respublikasi Davlat Xizmatlari Reyestri yoki Soliq Ochiq API (yoki STIR - INN orqali) integratsiyasi qilish orqali, u yerdan ro'yxatdan o'tgan sanani olib real oylarga hisoblaydigan API xizmati yoziladi.
- **`sameAddress` (Bir xil manzil/IP):** Fraud (firibgarlik) holatini aniqlash uchun tender ishtirokchilari manzillari aniqlanadi: `Qatnashchi A manzili == Qatnashchi B manzili` ekanligi real taqqoslanadi.

## 2. Bozor o'rtacha narxi (`marketAvg`) va Machine Learning
Hozir asosan formulada hisoblanmoqda (`marketAvg = amount / random(1.2 - 2.5)`). Buni mashina o'rganish (Machine Learning) ga almashtiramiz:

**Qo'llaniladigan Model:** Random Forest yoki Gradient Boosting (XGBoost/LightGBM).

- **O'rgatish Bosqichi (Training):** 1.py dagi kabi avvalgi barcha tugallangan va ishonchli bitimlarni tarixini (History CSV) bazaga yig'iladi. Shu turdagi oldingi "shprits", "ruchka" kabi kategoriyalar narxlanishi modelga kiritiladi (`Training set`). Model `X` (Kategoriya, Viloyat, Fasl/Oy) ga asoslanib `Y` (Kutish mumkin bo'lgan O'rtacha Narx - marketAvg) ni bashorat qiladi (Predict).
- **Inference (Ishlash):** Backend UZEX'dan yangi kelgan ma'lumotlarni ML Service'ga (alohida PyTorch/Sklearn microservice) tashlaydi va natijani aniqlaydi.

## 3. Graph-Based Fraud Detection System (Kelajak Arxitekturasi)
Ayni paytdagi tender tizimlarida Qatnashchilarni aniqlash oson emas. Bizning tizimda Neo4j (Graph Databaza) orqali kishilar (Ta'sischilar, Rahbarlar) va Kompaniyalar o'rtasida aloqalarni (Connections) vizualizatsiya qilamiz. Agar turli Qatnashchilar ORQASIDA bitta Ta'sischi / Qurilma IP'si turganini bilsak, Fraud Risk (Qizil Signal) avtomatik 99% qilinadi.

Ushbu qadamlarning dastlabkisi uchun backend tayyor (`schemas.py` da ishtirokchilar INN bilan qo'shilgan, shunchaki real soliqchi API'sini almashtirish qoldi xolos).
