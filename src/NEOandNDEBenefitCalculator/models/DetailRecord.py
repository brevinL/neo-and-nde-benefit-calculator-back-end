from .Instruction import Instruction

class DetailRecord(object):
	def __init__(self, person_id, earliest_retirement_age_instructions=None, normal_retirement_age_instructions=None, 
		average_indexed_monthly_covered_earning_instructions=None, basic_primary_insurance_amount_instructions=None, 
		wep_primary_insurance_amount_instructions=None, average_indexed_monthly_non_covered_earning_instructions=None, 
		monthly_non_covered_pension_instructions=None, wep_reduction_instructions=None, 
		final_primary_insurance_amount_instructions=None, delay_retirement_credit_instructions=None, 
		early_retirement_reduction_instructions=None, benefit_instructions=None, 
		government_pension_offset_instructions=None, spousal_insurance_benefit_instructions=None, 
		survivor_insurance_benefit_instructions=None):
		self.person_id = person_id
		self.earliest_retirement_age_instructions = earliest_retirement_age_instructions
		self.normal_retirement_age_instructions = normal_retirement_age_instructions
		self.average_indexed_monthly_covered_earning_instructions = average_indexed_monthly_covered_earning_instructions
		self.basic_primary_insurance_amount_instructions = basic_primary_insurance_amount_instructions
		self.wep_primary_insurance_amount_instructions = wep_primary_insurance_amount_instructions
		self.average_indexed_monthly_non_covered_earning_instructions = average_indexed_monthly_non_covered_earning_instructions
		self.monthly_non_covered_pension_instructions = monthly_non_covered_pension_instructions
		self.wep_reduction_instructions = wep_reduction_instructions
		self.final_primary_insurance_amount_instructions = final_primary_insurance_amount_instructions
		self.delay_retirement_credit_instructions = delay_retirement_credit_instructions
		self.early_retirement_reduction_instructions = early_retirement_reduction_instructions
		self.benefit_instructions = benefit_instructions
		self.government_pension_offset_instructions = government_pension_offset_instructions
		self.spousal_insurance_benefit_instructions = spousal_insurance_benefit_instructions
		self.survivor_insurance_benefit_instructions = survivor_insurance_benefit_instructions

# from django.db import models
# from BenefitRule.models import Record

# class DetailRecord(Record):
# 	earliest_retirement_age_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="earliest_retirement_age_instructions") 
# 	normal_retirement_age_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="normal_retirement_age_instructions") 
# 	average_indexed_monthly_covered_earning_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_covered_earning_instructions") 
# 	basic_primary_insurance_amount_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="basic_primary_insurance_amount_instructions") 
# 	wep_primary_insurance_amount_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="wep_primary_insurance_amount_instructions") 
# 	average_indexed_monthly_non_covered_earning_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_non_covered_earning_instructions") 
# 	monthly_non_covered_pension_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="monthly_non_covered_pension_instructions") 
# 	wep_reduction_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="wep_reduction_instructions") 
# 	final_primary_insurance_amount_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="final_primary_insurance_amount_instructions")
# 	delay_retirement_credit_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="delay_retirement_credit_instructions")
# 	early_retirement_reduction_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="early_retirement_reduction_instructions")
# 	benefit_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="benefit_instructions") 
# 	government_pension_offset_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="government_pension_offset_instructions")
# 	spousal_insurance_benefit_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="spousal_insurance_benefit_instructions") 
# 	survivor_insurance_benefit_instructions = models.ManyToManyField(Instruction, on_delete=models.CASCADE, null=True, related_name="survivor_insurance_benefit_instructions") 