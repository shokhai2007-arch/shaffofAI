from rest_framework import serializers
from .models import Tender, Participant

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['name', 'role', 'type', 'director', 'address', 'ageMonths']

class TenderSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    id = serializers.CharField(source='lot_id', read_only=True)

    class Meta:
        model = Tender
        fields = [
            'id', 'lot_id', 'name', 'org', 'region', 'sector', 'date', 
            'amount', 'marketAvg', 'companyAgeMonths', 'sameAddress',
            'score', 'riskLevel', 'riskLabel', 'riskColor', 'factors',
            'participants'
        ]
