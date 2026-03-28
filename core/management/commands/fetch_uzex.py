from django.core.management.base import BaseCommand
import requests
from core.models import Tender, Participant
from core.utils import API_CONFIGS, HEADERS, generate_mock_fields, generate_fake_participants, parse_date

class Command(BaseCommand):
    help = 'Fetches completed deals from UZEX and populates the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of records to fetch across APIs'
        )

    def handle(self, *args, **options):
        max_records = options['limit']
        total_fetched = 0

        self.stdout.write("API dan boshlang'ich ma'lumotlarni olyapmiz...")

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
                        
                        if Tender.objects.filter(lot_id=t_id).exists():
                            continue
                            
                        t_name = item.get("product_name") or item.get("category_name", "")
                        t_org = item.get("customer_name", "")
                        t_region = item.get("customer_region_name") or item.get("customer_region", "")
                        t_sector = item.get("category_name", "")
                        t_date = parse_date(item.get("deal_date", ""))
                        t_amount = float(item.get("deal_cost", 0))

                        mock_data = generate_mock_fields(t_amount)

                        db_tender = Tender.objects.create(
                            lot_id=t_id,
                            name=t_name,
                            org=t_org,
                            region=t_region,
                            sector=t_sector,
                            date=t_date,
                            amount=t_amount,
                            **mock_data
                        )
                        
                        prov_name = item.get("provider_name", "Noma'lum provayder")
                        prov_inn = str(item.get("provider_inn", ""))
                        
                        Participant.objects.create(
                            tender=db_tender,
                            name=prov_name,
                            inn=prov_inn,
                            role="G'olib",
                            type="company",
                            director="Real Director (Mock)", 
                            address="Real Address (Mock)",
                            ageMonths=mock_data["companyAgeMonths"]
                        )
                        
                        fake_parts = generate_fake_participants()
                        participants_to_create = [
                            Participant(
                                tender=db_tender,
                                name=fake_p["name"],
                                inn=fake_p["inn"],
                                role=fake_p["role"],
                                type=fake_p["type"],
                                director=fake_p["director"],
                                address=fake_p["address"],
                                ageMonths=fake_p["ageMonths"]
                            ) for fake_p in fake_parts
                        ]
                        Participant.objects.bulk_create(participants_to_create)
                            
                        total_fetched += 1
                
            except Exception as e:
                self.stderr.write(f"Xatolik API da {config['url']}: {e}")
                pass

        self.stdout.write(self.style.SUCCESS(f"Muvaffaqiyatli {total_fetched} ma'lumot olindi."))
