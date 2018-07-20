from django.db import models

class BenefitRule(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()