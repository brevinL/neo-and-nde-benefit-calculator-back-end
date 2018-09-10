from django.db import models
from BenefitRule.models import Earning

class RecordManager(models.Manager):
	def calculate_annual_covered_earnings(self, earnings):
		annual_covered_earnings = earnings.filter(type_of_earning=Earning.COVERED, time_period=Earning.YEARLY)
		return annual_covered_earnings

	def calculate_average_indexed_monthly_covered_earning(self, aime_law, taxable_earnings):
		average_indexed_monthly_covered_earning = aime_law.calculate(taxable_earnings=taxable_earnings) 
		average_indexed_monthly_covered_earning.save()
		return average_indexed_monthly_covered_earning

	def calculate_annual_non_covered_earnings(self, earnings):
		annual_non_covered_earnings = earnings.filter(type_of_earning=Earning.NONCOVERED, time_period=Earning.YEARLY)
		return annual_non_covered_earnings

	def calculate_retirement_record(self, benefit_rules, respondent):
		earliest_retirement_age = self.calculate_earliest_retirement_age(
			earliest_retirement_age_law=benefit_rules.earliest_retirement_age_law,
			year_of_birth=respondent.year_of_birth)
		normal_retirement_age = self.calculate_normal_retirement_age(
			normal_retirement_age_law=benefit_rules.normal_retirement_age_law,
			year_of_birth=respondent.year_of_birth)
		annual_covered_earnings = self.calculate_annual_covered_earnings(earnings=respondent.earning_set)
		average_indexed_monthly_covered_earning = self.calculate_average_indexed_monthly_covered_earning(
			aime_law=benefit_rules.aime_law,
			taxable_earnings=respondent.annual_covered_earnings) 
		basic_primary_insurance_amount = self.calculate_basic_primary_insurance_amount(
			pia_law=benefit_rules.pia_law,
			average_indexed_monthly_earning=average_indexed_monthly_covered_earning)
		wep_primary_insurance_amount = self.calculate_wep_primary_insurance_amount(
			wep_pia_law=benefit_rules.wep_pia_law, 
			year_of_coverage=annual_covered_earnings.count())
		annual_non_covered_earnings = self.calculate_annual_non_covered_earnings(earnings=respondent.earning_set)
		average_indexed_monthly_non_covered_earning = self.calculate_average_indexed_monthly_non_covered_earning(
			aime_law=benefit_rules.aime_law, 
			taxable_earnings=annual_non_covered_earnings)
		# monthly_non_covered_pension = average_indexed_monthly_non_covered_earning * respondent.fraction_of_non_covered_aime_to_non_covered_pension
		government_pension_offset = self.calculate_government_pension_offset(
			gpo_law=benefit_rules.gpo_law, 
			monthly_non_covered_pension=monthly_non_covered_pension)
		wep_reduction = self.calculate_wep_reduction(
			wep_law=benefit_rules.wep_law, 
			primary_insurance_amount=basic_primary_insurance_amount, 
			wep_primary_insurance_amount=wep_primary_insurance_amount, 
			monthly_non_covered_pension=monthly_non_covered_pension)
		final_primary_insurance_amount = self.calculate_final_primary_insurance_amount(
			basic_primary_insurance_amount=basic_primary_insurance_amount, 
			wep_reduction=wep_reduction)
		max_delay_retirement_credit = self.calculate_max_delay_retirement_credit(
			drc_law=benefit_rules.drc_law, 
			year_of_birth=respondent.year_of_birth, 
			normal_retirement_age=normal_retirement_age)
		delay_retirement_credit = self.calculate_delay_retirement_credit(
			drc_law=benefit_rules.drc_law, 
			year_of_birth=respondent.year_of_birth, 
			normal_retirement_age=normal_retirement_age, 
			retirement_age=respondent.retirement_age,
			max_delay_retirement_credit=max_delay_retirement_credit)
		max_early_retirement_reduction = self.calculate_max_early_retirement_reduction(
			primary_err_law=benefit_rules.primary_err_law, 
			normal_retirement_age=normal_retirement_age, 
			earliest_retirement_age=earliest_retirement_age)
		early_retirement_reduction = self.calculate_early_retirement_reduction(
			primary_err_law=benefit_rules.primary_err_law, 
			normal_retirement_age=normal_retirement_age, 
			retirement_age=respondent.retirement_age, 
			max_early_retirement_reduction=max_early_retirement_reduction)
		benefit = self.calculate_benefit(
			final_primary_insurance_amount=final_primary_insurance_amount, 
			delay_retirement_credit=delay_retirement_credit, 
			early_retirement_reduction=early_retirement_reduction)

		return self.create_or_update_record(
			earliest_retirement_age=earliest_retirement_age,
			normal_retirement_age=normal_retirement_age,
			average_indexed_monthly_covered_earning=average_indexed_monthly_covered_earning,
			basic_primary_insurance_amount=basic_primary_insurance_amount,
			wep_primary_insurance_amount=wep_primary_insurance_amount,
			average_indexed_monthly_non_covered_earning=average_indexed_monthly_non_covered_earning,
			monthly_non_covered_pension=monthly_non_covered_pension,
			government_pension_offset=government_pension_offset,
			wep_reduction=wep_reduction,
			final_primary_insurance_amount=final_primary_insurance_amount,
			max_delay_retirement_credit=max_delay_retirement_credit,
			delay_retirement_credit=delay_retirement_credit,
			max_early_retirement_reduction=max_early_retirement_reduction,
			early_retirement_reduction=early_retirement_reduction,
			benefit=benefit)

	def calculate_dependent_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record):
		beneficiary_record.spousal_insurance_benefit = benefit_rules.spousal_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount,
			government_pension_offset=beneficiary_record.government_pension_offset)
		beneficiary_record.spousal_insurance_benefit.save()
		return beneficiary_record

	def calculate_survivor_benefits(self, benefit_rules, respondent, beneficiary_record, spousal_beneficiary_record):
		survivor_early_retirement_reduction = benefit_rules.survivor_insurance_benefit_law.calculateSurvivorEarlyRetirementReductionFactor(
			normal_retirement_age=beneficiary_record.normal_retirement_age,
			retirement_age=respondent.retirement_age)
		beneficiary_record.survivor_insurance_benefit = benefit_rules.survivor_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_record.benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=survivor_early_retirement_reduction, 
			spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
			government_pension_offset=beneficiary_record.government_pension_offset)
		beneficiary_record.survivor_insurance_benefit.save()
		return beneficiary_record