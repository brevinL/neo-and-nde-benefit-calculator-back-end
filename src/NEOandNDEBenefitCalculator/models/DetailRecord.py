from django.db import models
from BenefitRule.models import Task
from NEOandNDEBenefitCalculator.managers import DetailRecordManager

class DetailRecord(DetailRecord):
	monthly_non_covered_pension_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="monthly_non_covered_pension_task") 

	objects = DetailRecordManager()