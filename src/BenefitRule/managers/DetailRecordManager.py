from django.db import models
from BenefitRule.models import Task, percentage
from django.db.models import Max

# issue: populates too many and redundated instructions
class DetailRecordManager(models.Manager):
	def create_average_indexed_monthly_covered_earning_task(aime_law, taxable_earnings):
		return aime_law.stepByStep(taxable_earnings=taxable_earnings)

	def create_basic_primary_insurance_amount_task(pia_law, average_indexed_monthly_earning, year_of_coverage):
		return pia_law.stepByStep(
			average_indexed_monthly_earning=average_indexed_monthly_earning, 
			year_of_coverage=year_of_coverage)

	def create_wep_primary_insurance_amount_task(wep_pia_law, average_indexed_monthly_earning, year_of_coverage):
		return wep_pia_law.stepByStep(
			average_indexed_monthly_earning=average_indexed_monthly_earning,
			year_of_coverage=year_of_coverage)

	def create_average_indexed_monthly_non_covered_earning_task(aime_law, taxable_earnings):
		return aime_law.stepByStep(taxable_earnings=taxable_earnings)

	def create_government_pension_offset_task(gpo_law, monthly_non_covered_pension):
		return gpo_law.stepByStep(monthly_non_covered_pension=monthly_non_covered_pension)

	def create_wep_reduction_task(wep_law, primary_insurance_amount, wep_primary_insurance_amount, monthly_non_covered_pension):
		return wep_law.stepByStep(
			primary_insurance_amount=primary_insurance_amount, 
			wep_primary_insurance_amount=wep_primary_insurance_amount,
			monthly_non_covered_pension=monthly_non_covered_pension)

	def create_final_primary_insurance_amount_task(basic_primary_insurance_amount, wep_reduction, final_primary_insurance_amount):
		final_primary_insurance_amount_task = Task.objects.create()
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Get primary insurance amount', order=1)
		instruction.expression_set.create(description=f'primary insurance amount = {basic_primary_insurance_amount}', order=1)
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Get windfall elimination provision amount', order=2)
		instruction.expression_set.create(description=f'windfall elimination provision amount = {wep_reduction}', order=1)
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Recalculate primary insurance amount by reducing the primary insurance amount with the windfall elimination provision amount', order=3)
		instruction.expression_set.create(description='primary insurance amount  = primary insurance amount - windfall elimination provision', order=1)
		instruction.expression_set.create(description=f'primary insurance amount  = {basic_primary_insurance_amount} - {wep_reduction}', order=2)
		instruction.expression_set.create(description=f'primary insurance amount = {final_primary_insurance_amount}', order=3)

		return final_primary_insurance_amount_task

	def create_delay_retirement_credit_task(drc_law, year_of_birth, normal_retirement_age, max_delay_retirement_credit, delay_retirement_credit):
		delay_retirement_credit_task = drc_law.stepByStep(
			year_of_birth=year_of_birth, 
			normal_retirement_age=normal_retirement_age, 
			delayed_retirement_age=drc_law.age_limit)
		return delay_retirement_credit_task

	def create_early_retirement_reduction_task(primary_err_law, normal_retirement_age, earliest_retirement_age, max_early_retirement_reduction, early_retirement_reduction):
		early_retirement_reduction_task = primary_err_law.stepByStep(normal_retirement_age=normal_retirement_age, 
			early_retirement_age=earliest_retirement_age)
		return early_retirement_reduction_task

	def create_benefit_task(delay_retirement_credit, early_retirement_reduction, final_primary_insurance_amount, benefit):
		benefit_task = Task.objects.create()
		instruction = benefit_task.instruction_set.create(description='Get delay retirement credit', order=1)
		instruction.expression_set.create(description=f'delay retirement credit = {percentage(delay_retirement_credit)}', order=1)
		instruction = benefit_task.instruction_set.create(description='Get early retirement reduction', order=2)
		instruction.expression_set.create(description=f'early retirement reduction = {percentage(early_retirement_reduction)}', order=1)
		instruction = benefit_task.instruction_set.create(description='Get primary insurance amount', order=3)
		instruction.expression_set.create(description=f'primary insurance amount = {final_primary_insurance_amount}', order=1)
		instruction = benefit_task.instruction_set.create(description='Calculate benefit', order=4)
		instruction.expression_set.create(description='benefit = primary insurance amount x (1 + (delay retirement credit + early retirement reduction))', order=1)
		instruction.expression_set.create(description=f'benefit = {final_primary_insurance_amount} x (1 + ({percentage(delay_retirement_credit)} + {percentage(early_retirement_reduction)}))', order=2)
		instruction.expression_set.create(description=f'benefit = {final_primary_insurance_amount} x {percentage(1 + (delay_retirement_credit + early_retirement_reduction))}', order=3)
		instruction.expression_set.create(description=f'benefit = {benefit}', order=3)

		return benefit_task

	def calculate_retirement_record(self, benefit_rules, person, beneficiary_record):
		average_indexed_monthly_covered_earning_task = self.create_average_indexed_monthly_covered_earning_task(
			aime_law=benefit_rules.aime_law,
			taxable_earnings=person.annual_covered_earnings)
		basic_primary_insurance_amount_task = self.create_basic_primary_insurance_amount_task(
			pia_law=benefit_rules.pia_law,
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning, 
			year_of_coverage=0)
		wep_primary_insurance_amount_task = self.create_wep_primary_insurance_amount_task(
			wep_pia_law=benefit_rules.wep_pia_law,
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning,
			year_of_coverage=person.years_of_covered_earnings)
		average_indexed_monthly_non_covered_earning_task = self.create_average_indexed_monthly_non_covered_earning_task(
			aime_law=benefit_rules.aime_law,
			taxable_earnings=person.annual_non_covered_earnings)
		government_pension_offset_task = self.create_government_pension_offset_task(
			gpo_law=benefit_rules.gpo_law, 
			monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)
		wep_reduction_task = self.create_wep_reduction_task(
			wep_law=benefit_rules.wep_law,
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			wep_primary_insurance_amount=beneficiary_record.wep_primary_insurance_amount,
			monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)
		final_primary_insurance_amount_task = self.create_final_primary_insurance_amount_task(
			basic_primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount,
			wep_reduction=beneficiary_record.wep_reduction,
			final_primary_insurance_amount=beneficiary_record.final_primary_insurance_amount)
		delay_retirement_credit_task = self.create_delay_retirement_credit_task(
			drc_law=benefit_rules.drc_law,
			year_of_birth=person.year_of_birth, 
			normal_retirement_age=beneficiary_record.normal_retirement_age, 
			respondent_delay_retirement_credit=beneficiary_record.delay_retirement_credit,
			delay_retirement_credit=beneficiary_record.delay_retirement_credit, 
			max_delay_retirement_credit=beneficiary_record.max_delay_retirement_credit)
		early_retirement_reduction_task = self.create_early_retirement_reduction_task(
			primary_err_law=benefit_rules.primary_err_law,
			normal_retirement_age=beneficiary_record.normal_retirement_age,
			earliest_retirement_age=beneficiary_record.earliest_retirement_age,
			respondent_early_retirement_reduction=beneficiary_record.early_retirement_reduction,
			max_early_retirement_reduction=beneficiary_record.max_early_retirement_reduction,
			early_retirement_reduction=beneficiary_record.early_retirement_reduction)
		benefit_task = self.create_benefit_task(
			delay_retirement_credit=beneficiary_record.delay_retirement_credit, 
			early_retirement_reduction=beneficiary_record.early_retirement_reduction, 
			final_primary_insurance_amount=beneficiary_record.final_primary_insurance_amount, 
			benefit=beneficiary_record.benefit)

		return self.create_or_update_detail_record(average_indexed_monthly_covered_earning_task=average_indexed_monthly_covered_earning_task,
				basic_primary_insurance_amount_task=basic_primary_insurance_amount_task,
				wep_primary_insurance_amount_task=wep_primary_insurance_amount_task,
				average_indexed_monthly_non_covered_earning_task=average_indexed_monthly_non_covered_earning_task,
				government_pension_offset_task=government_pension_offset_task,
				wep_reduction_task=wep_reduction_task,
				final_primary_insurance_amount_task=final_primary_insurance_amount_task,
				delay_retirement_credit_task=delay_retirement_credit_task,
				early_retirement_reduction_task=early_retirement_reduction_task,
				benefit_task=benefit_task)

	def create_or_update_detail_record(self,
		average_indexed_monthly_covered_earning_task=None,
		basic_primary_insurance_amount_task=None,
		wep_primary_insurance_amount_task=None,
		average_indexed_monthly_non_covered_earning_task=None,
		government_pension_offset_task=None,
		wep_reduction_task=None,
		final_primary_insurance_amount_task=None,
		delay_retirement_credit_task=None,
		early_retirement_reduction_task=None,
		benefit_task=None):
		try:
			detail_record = DetailRecord.objects.get(person=person)
			if not average_indexed_monthly_covered_earning_task is None:
				detail_record.average_indexed_monthly_covered_earning_task = average_indexed_monthly_covered_earning_task
			if not basic_primary_insurance_amount_task is None:
				detail_record.basic_primary_insurance_amount_task = basic_primary_insurance_amount_task
			if not wep_primary_insurance_amount_task is None:
				detail_record.wep_primary_insurance_amount_task = wep_primary_insurance_amount_task
			if not average_indexed_monthly_non_covered_earning_task is None:
				detail_record.average_indexed_monthly_non_covered_earning_task = average_indexed_monthly_non_covered_earning_task
			if not government_pension_offset_task is None:
				detail_record.government_pension_offset_task = government_pension_offset_task
			if not wep_reduction_task is None:
				detail_record.wep_reduction_task = wep_reduction_task
			if not final_primary_insurance_amount_task is None:
				detail_record.final_primary_insurance_amount_task = final_primary_insurance_amount_task
			if not delay_retirement_credit_task is None:
				detail_record.delay_retirement_credit_task = delay_retirement_credit_task
			if not early_retirement_reduction_task is None:
				detail_record.early_retirement_reduction_task = early_retirement_reduction_task
			if not benefit_task is None:
				detail_record.benefit_task = benefit_task
			detail_record.save()
		except DetailRecord.DoesNotExist:
			detail_record = self.create(
				person=person,
				average_indexed_monthly_covered_earning_task=average_indexed_monthly_covered_earning_task,
				basic_primary_insurance_amount_task=basic_primary_insurance_amount_task,
				wep_primary_insurance_amount_task=wep_primary_insurance_amount_task,
				average_indexed_monthly_non_covered_earning_task=average_indexed_monthly_non_covered_earning_task,
				government_pension_offset_task=government_pension_offset_task,
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

	def calculate_survivor_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record, detail_record):
		detail_record.survivor_insurance_benefit_task = benefit_rules.survivor_insurance_benefit_law.stepByStep(
			primary_insurance_amount=beneficiary_record.benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=beneficiary_record.survivor_early_retirement_reduction, #
			spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
			government_pension_offset=beneficiary_record.government_pension_offset)
		detail_record.save()
		return detail_record