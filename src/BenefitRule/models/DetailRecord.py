from django.db import models
from BenefitRule.models import Person, Task

from BenefitRule.managers import DetailRecordManager

class DetailRecord(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	average_indexed_monthly_covered_earning_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_covered_earning_task") 
	basic_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="basic_primary_insurance_amount_task") 
	wep_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="wep_primary_insurance_amount_task") 
	average_indexed_monthly_non_covered_earning_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_non_covered_earning_task") 
	wep_reduction_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="wep_reduction_task") 
	final_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="final_primary_insurance_amount_task")
	delay_retirement_credit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="delay_retirement_credit_task")
	early_retirement_reduction_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="early_retirement_reduction_task")
	benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="benefit_task") 
	government_pension_offset_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="government_pension_offset_task")
	spousal_insurance_benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="spousal_insurance_benefit_task") 
	survivor_insurance_benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="survivor_insurance_benefit_task") 

	objects = DetailRecordManager()