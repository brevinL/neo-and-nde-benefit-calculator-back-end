from django.db import models
from BenefitRule.models import Person, Task, percentage
from django.db.models import Max

# issue: populates too many and redundated instructions
class DetailRecordManager(models.Manager):
	def calculate_retirement_record(self, benefit_rules, respondent, beneficiary_record):
		# earliest_retirement_age_task = earliest_retirement_age_law.stepByStep(year_of_birth=respondent.year_of_birth)
		# normal_retirement_age_task = normal_retirement_age_law.stepByStep(year_of_birth=respondent.year_of_birth)
		average_indexed_monthly_covered_earning_task = benefit_rules.aime_law.stepByStep(taxable_earnings=respondent.annual_covered_earnings)
		basic_primary_insurance_amount_task = benefit_rules.pia_law.stepByStep(
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning, 
			year_of_coverage=0)
		wep_primary_insurance_amount_task = benefit_rules.wep_pia_law.stepByStep(
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning,
			year_of_coverage=respondent.years_of_covered_earnings)
		average_indexed_monthly_non_covered_earning_task = benefit_rules.aime_law.stepByStep(taxable_earnings=respondent.annual_non_covered_earnings)
		government_pension_offset_task = benefit_rules.gpo_law.stepByStep(monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)

		monthly_non_covered_pension_task = Task.objects.create()
		instruction = monthly_non_covered_pension_task.instruction_set.create(description='Get average indexed monthly non covered earning', order=1)
		instruction.expression_set.create(description=f'average indexed monthly non covered earning = {beneficiary_record.average_indexed_monthly_non_covered_earning}', order=1)
		instruction = monthly_non_covered_pension_task.instruction_set.create(description='Get fraction of non covered AIME to non covered pension', order=2)
		instruction.expression_set.create(description=f'fraction of non covered AIME to non covered pension = {respondent.fraction_of_non_covered_aime_to_non_covered_pension}', order=1)
		instruction = monthly_non_covered_pension_task.instruction_set.create(description='Multiply average indexed monthly non covered earning with the fraction that was coverted from non covered AIME to non covered pension', order=3)
		instruction.expression_set.create(description='monthly_non_covered_pension = average indexed monthly non covered earning x fraction of non covered AIME to non covered pension', order=1)
		instruction.expression_set.create(description=f'monthly_non_covered_pension = {beneficiary_record.average_indexed_monthly_non_covered_earning} x {respondent.fraction_of_non_covered_aime_to_non_covered_pension}', order=2)
		instruction.expression_set.create(description=f'monthly_non_covered_pension = {beneficiary_record.monthly_non_covered_pension}', order=3)

		wep_reduction_task = benefit_rules.wep_law.stepByStep(
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			wep_primary_insurance_amount=beneficiary_record.wep_primary_insurance_amount,
			monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)

		final_primary_insurance_amount_task = Task.objects.create()
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Get primary insurance amount', order=1)
		instruction.expression_set.create(description=f'primary insurance amount = {beneficiary_record.basic_primary_insurance_amount}', order=1)
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Get windfall elimination provision amount', order=2)
		instruction.expression_set.create(description=f'windfall elimination provision amount = {beneficiary_record.wep_reduction}', order=1)
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Recalculate primary insurance amount by reducing the primary insurance amount with the windfall elimination provision amount', order=3)
		instruction.expression_set.create(description='primary insurance amount  = primary insurance amount - windfall elimination provision', order=1)
		instruction.expression_set.create(description=f'primary insurance amount  = {beneficiary_record.basic_primary_insurance_amount} - {beneficiary_record.wep_reduction}', order=2)
		instruction.expression_set.create(description=f'primary insurance amount = {beneficiary_record.final_primary_insurance_amount}', order=3)

		delay_retirement_credit_task = benefit_rules.drc_law.stepByStep(
			year_of_birth=respondent.year_of_birth, 
			normal_retirement_age=beneficiary_record.normal_retirement_age, 
			delayed_retirement_age=benefit_rules.drc_law.age_limit)
		order = delay_retirement_credit_task.instruction_set.aggregate(Max('order')).get('order__max')
		instruction = delay_retirement_credit_task.instruction_set.create(description='Get respondent\'s delay retirement credit', order=order+1)
		instruction.expression_set.create(description=f'respondent\'s delay retirement credit = {percentage(respondent.delay_retirement_credit)}', order=1)
		instruction = delay_retirement_credit_task.instruction_set.create(description='Cap Delay Retirement Credit', order=order+2)
		instruction.expression_set.create(description='delay retirement credit = min(max delay retirement credit, respondent\'s delay retirement credit', order=1)
		instruction.expression_set.create(description=f'delay retirement credit = min({percentage(beneficiary_record.max_delay_retirement_credit)}, {percentage(respondent.delay_retirement_credit)})', order=2)
		instruction.expression_set.create(description=f'delay retirement credit = {percentage(beneficiary_record.delay_retirement_credit)}', order=3) 

		early_retirement_reduction_task = benefit_rules.primary_err_law.stepByStep(normal_retirement_age=beneficiary_record.normal_retirement_age, 
			early_retirement_age=beneficiary_record.earliest_retirement_age)
		order = early_retirement_reduction_task.instruction_set.aggregate(Max('order')).get('order__max')
		instruction = early_retirement_reduction_task.instruction_set.create(description='Get respondent\'s early retirement reduction', order=order+1)
		instruction.expression_set.create(description=f'respondent\'s early retirement reduction = {percentage(respondent.early_retirement_reduction)}', order=1)
		instruction = early_retirement_reduction_task.instruction_set.create(description='Cap Delay Retirement Credit', order=order+2)
		instruction.expression_set.create(description='early retirement reduction = min(max early retirement reduction, respondent\'s early retirement reduction', order=1)
		instruction.expression_set.create(description=f'early retirement reduction = min({percentage(beneficiary_record.max_early_retirement_reduction)}, {percentage(respondent.early_retirement_reduction)})', order=2)
		instruction.expression_set.create(description=f'early retirement reduction = {percentage(beneficiary_record.early_retirement_reduction)}', order=3)

		benefit_task = Task.objects.create()
		instruction = benefit_task.instruction_set.create(description='Get delay retirement credit', order=1)
		instruction.expression_set.create(description=f'delay retirement credit = {percentage(beneficiary_record.delay_retirement_credit)}', order=1)
		instruction = benefit_task.instruction_set.create(description='Get early retirement reduction', order=2)
		instruction.expression_set.create(description=f'early retirement reduction = {percentage(beneficiary_record.early_retirement_reduction)}', order=1)
		instruction = benefit_task.instruction_set.create(description='Get primary insurance amount', order=3)
		instruction.expression_set.create(description=f'primary insurance amount = {beneficiary_record.final_primary_insurance_amount}', order=1)
		instruction = benefit_task.instruction_set.create(description='Calculate benefit', order=4)
		instruction.expression_set.create(description='benefit = primary insurance amount x (1 + (delay retirement credit + early retirement reduction))', order=1)
		instruction.expression_set.create(description=f'benefit = {beneficiary_record.final_primary_insurance_amount} x (1 + ({percentage(beneficiary_record.delay_retirement_credit)} + {percentage(beneficiary_record.early_retirement_reduction)}))', order=2)
		instruction.expression_set.create(description=f'benefit = {beneficiary_record.final_primary_insurance_amount} x {percentage(1 + (beneficiary_record.delay_retirement_credit + beneficiary_record.early_retirement_reduction))}', order=3)
		instruction.expression_set.create(description=f'benefit = {beneficiary_record.benefit}', order=3)

		try:
			detail_record = DetailRecord.objects.get(person=respondent)
			detail_record.average_indexed_monthly_covered_earning_task = average_indexed_monthly_covered_earning_task
			detail_record.basic_primary_insurance_amount_task = basic_primary_insurance_amount_task
			detail_record.wep_primary_insurance_amount_task = wep_primary_insurance_amount_task
			detail_record.average_indexed_monthly_non_covered_earning_task = average_indexed_monthly_non_covered_earning_task
			detail_record.government_pension_offset_task = government_pension_offset_task
			detail_record.monthly_non_covered_pension_task = monthly_non_covered_pension_task
			detail_record.wep_reduction_task = wep_reduction_task
			detail_record.final_primary_insurance_amount_task = final_primary_insurance_amount_task
			detail_record.delay_retirement_credit_task = delay_retirement_credit_task
			detail_record.early_retirement_reduction_task = early_retirement_reduction_task
			detail_record.benefit_task = benefit_task
			detail_record.save()
		except DetailRecord.DoesNotExist:
			detail_record = self.create(
				person=respondent,
				average_indexed_monthly_covered_earning_task=average_indexed_monthly_covered_earning_task,
				basic_primary_insurance_amount_task=basic_primary_insurance_amount_task,
				wep_primary_insurance_amount_task=wep_primary_insurance_amount_task,
				average_indexed_monthly_non_covered_earning_task=average_indexed_monthly_non_covered_earning_task,
				government_pension_offset_task=government_pension_offset_task,
				monthly_non_covered_pension_task=monthly_non_covered_pension_task,
				wep_reduction_task=wep_reduction_task,
				final_primary_insurance_amount_task=final_primary_insurance_amount_task,
				delay_retirement_credit_task=delay_retirement_credit_task,
				early_retirement_reduction_task=early_retirement_reduction_task,
				benefit_task=benefit_task)

		return detail_record

	def calculate_dependent_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record, detail_record):
		detail_record.spousal_insurance_benefit_task = benefit_rules.spousal_insurance_benefit_law.stepByStep(
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount,
			government_pension_offset=beneficiary_record.government_pension_offset)
		detail_record.save()
		return detail_record

	def calculate_survivor_benefits(self, benefit_rules, respondent, beneficiary_record, spousal_beneficiary_record, detail_record):
		detail_record.survivor_insurance_benefit_task = benefit_rules.survivor_insurance_benefit_law.stepByStep(
			primary_insurance_amount=beneficiary_record.benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=respondent.survivor_early_retirement_reduction, 
			spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
			government_pension_offset=beneficiary_record.government_pension_offset)
		detail_record.save()
		return detail_record

class DetailRecord(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	# earliest_retirement_age_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="earliest_retirement_age_task") 
	# normal_retirement_age_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="normal_retirement_age_task") 
	average_indexed_monthly_covered_earning_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_covered_earning_task") 
	basic_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="basic_primary_insurance_amount_task") 
	wep_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="wep_primary_insurance_amount_task") 
	average_indexed_monthly_non_covered_earning_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_non_covered_earning_task") 
	monthly_non_covered_pension_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="monthly_non_covered_pension_task") 
	wep_reduction_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="wep_reduction_task") 
	final_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="final_primary_insurance_amount_task")
	delay_retirement_credit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="delay_retirement_credit_task")
	early_retirement_reduction_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="early_retirement_reduction_task")
	benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="benefit_task") 
	government_pension_offset_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="government_pension_offset_task")
	spousal_insurance_benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="spousal_insurance_benefit_task") 
	survivor_insurance_benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="survivor_insurance_benefit_task") 

	objects = DetailRecordManager()