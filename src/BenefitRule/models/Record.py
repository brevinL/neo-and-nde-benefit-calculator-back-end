from django.db import models
from .Money import Money
from .Person import Person
from BenefitRule.managers import RecordManager

class Record(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	earliest_retirement_age = models.PositiveSmallIntegerField(null=True)
	normal_retirement_age = models.PositiveSmallIntegerField(null=True)
	average_indexed_monthly_covered_earning = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_covered_earning") 
	basic_primary_insurance_amount = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="basic_primary_insurance_amount") 
	wep_primary_insurance_amount = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="wep_primary_insurance_amount") 
	average_indexed_monthly_non_covered_earning = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_non_covered_earning") 
	monthly_non_covered_pension = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="monthly_non_covered_pension") 
	wep_reduction = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="wep_reduction") 
	final_primary_insurance_amount = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="final_primary_insurance_amount")
	max_delay_retirement_credit = models.FloatField(null=True)
	delay_retirement_credit = models.FloatField(null=True)
	max_early_retirement_reduction = models.FloatField(null=True)
	early_retirement_reduction = models.FloatField(null=True)
	benefit = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="benefit") 
	government_pension_offset = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="government_pension_offset")
	spousal_insurance_benefit = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="spousal_insurance_benefit") 
	survivor_insurance_benefit = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="survivor_insurance_benefit") 

	objects = RecordManager()