from django.db import models

class Tender(models.Model):
    lot_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=500, db_index=True, null=True, blank=True)
    org = models.CharField(max_length=500, null=True, blank=True)
    region = models.CharField(max_length=200, null=True, blank=True)
    sector = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    amount = models.FloatField(default=0.0)
    
    marketAvg = models.FloatField(null=True, blank=True)
    companyAgeMonths = models.IntegerField(null=True, blank=True)
    sameAddress = models.BooleanField(default=False)
    
    score = models.IntegerField(default=0)
    riskLevel = models.CharField(max_length=20, default="low")
    riskLabel = models.CharField(max_length=50, default="Past Xavf")
    riskColor = models.CharField(max_length=20, default="#4caf50")
    
    factors = models.JSONField(null=True, blank=True, default=dict)
    
    def __str__(self):
        return f"Tender {self.lot_id}"

class Participant(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="participants")
    name = models.CharField(max_length=500, null=True, blank=True)
    inn = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    
    type = models.CharField(max_length=50, default="company")
    director = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    ageMonths = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name or "Participant"
