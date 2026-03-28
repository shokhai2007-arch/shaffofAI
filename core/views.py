from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Tender
from .serializers import TenderSerializer
from .utils import generate_notifications_for_tender, generate_warning_notifications, generate_system_notifications

@api_view(['GET'])
def read_tenders(request):
    skip = int(request.GET.get('skip', 0))
    limit = int(request.GET.get('limit', 100))
    tenders = Tender.objects.all()[skip:skip+limit]
    serializer = TenderSerializer(tenders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def read_tender(request, tender_id):
    try:
        tender = Tender.objects.get(lot_id=tender_id)
        serializer = TenderSerializer(tender)
        return Response(serializer.data)
    except Tender.DoesNotExist:
        return Response({"detail": "Tender not found"}, status=404)

@api_view(['GET'])
def read_notifications(request):
    tenders = Tender.objects.all()[:200]
    serializer = TenderSerializer(tenders, many=True)
    tenders_data = serializer.data
    
    all_notifs = []
    
    for t_data in tenders_data:
        all_notifs.extend(generate_notifications_for_tender(t_data))
        
    all_notifs.extend(generate_warning_notifications(tenders_data))
    all_notifs.extend(generate_system_notifications(len(tenders_data)))
        
    all_notifs = sorted(all_notifs, key=lambda x: x.get("severityScore", 0), reverse=True)
    
    return Response(all_notifs[:20])
