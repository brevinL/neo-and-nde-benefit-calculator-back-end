from django.db import models
from .Money import Money
from .Person import Person

class RecordManager(models.Manager):
	def calculate_retirement_record(self, benefit_rules, respondent):
		earliest_retirement_age = benefit_rules.earliest_retirement_age_law.calculate(year_of_birth=respondent.year_of_birth)
		normal_retirement_age = benefit_rules.normal_retirement_age_law.calculate(year_of_birth=respondent.year_of_birth)
		average_indexed_monthly_covered_earning = benefit_rules.aime_law.calculate(taxable_earnings=respondent.annual_covered_earnings)
		basic_primary_insurance_amount = benefit_rules.pia_law.calculate(
			average_indexed_monthly_earning=average_indexed_monthly_covered_earning, 
			year_of_coverage=0)
		wep_primary_insurance_amount = benefit_rules.wep_pia_law.calculate(
			average_indexed_monthly_earning=average_indexed_monthly_covered_earning,
			year_of_coverage=respondent.years_of_covered_earnings)
		average_indexed_monthly_non_covered_earning = benefit_rules.aime_law.calculate(taxable_earnings=respondent.annual_non_covered_earnings)
		monthly_non_covered_pension = average_indexed_monthly_non_covered_earning * respondent.fraction_of_non_covered_aime_to_non_covered_pension
		government_pension_offset = benefit_rules.gpo_law.calculate(monthly_non_covered_pension=monthly_non_covered_pension)
		wep_reduction = benefit_rules.wep_law.calculate(
			primary_insurance_amount=basic_primary_insurance_amount, 
			wep_primary_insurance_amount=wep_primary_insurance_amount,
			monthly_non_covered_pension=monthly_non_covered_pension)
		final_primary_insurance_amount = basic_primary_insurance_amount - wep_reduction
		max_delay_retirement_credit = benefit_rules.drc_law.calculate(
			year_of_birth=respondent.year_of_birth, 
			normal_retirement_age=normal_retirement_age, 
			delayed_retirement_age=benefit_rules.drc_law.age_limit)
		delay_retirement_credit = min(max_delay_retirement_credit, respondent.delay_retirement_credit)
		max_early_retirement_reduction = benefit_rules.primary_err_law.calculate(normal_retirement_age=normal_retirement_age, 
			early_retirement_age=earliest_retirement_age)
		early_retirement_reduction = min(max_early_retirement_reduction, respondent.early_retirement_reduction)
		benefit = final_primary_insurance_amount * (1 + (delay_retirement_credit - early_retirement_reduction))

		# save here because calculate method is temp and depend if we have to save or not whereas here we want record to record everything
		average_indexed_monthly_covered_earning.save()
		basic_primary_insurance_amount.save()
		wep_primary_insurance_amount.save()
		average_indexed_monthly_non_covered_earning.save()
		monthly_non_covered_pension.save()
		government_pension_offset.save()
		wep_reduction.save()
		final_primary_insurance_amount.save()
		benefit.save()

		try:
			record = Record.objects.get(person=respondent)
			record.earliest_retirement_age = earliest_retirement_age
			record.normal_retirement_age = normal_retirement_age
			record.average_indexed_monthly_covered_earning = average_indexed_monthly_covered_earning
			record.basic_primary_insurance_amount = basic_primary_insurance_amount
			record.wep_primary_insurance_amount = wep_primary_insurance_amount
			record.average_indexed_monthly_non_covered_earning = average_indexed_monthly_non_covered_earning
			record.monthly_non_covered_pension = monthly_non_covered_pension
			record.government_pension_offset = government_pension_offset
			record.wep_reduction = wep_reduction
			record.final_primary_insurance_amount = final_primary_insurance_amount
			record.max_delay_retirement_credit = max_delay_retirement_credit
			record.delay_retirement_credit = delay_retirement_credit
			record.max_early_retirement_reduction = max_early_retirement_reduction
			record.early_retirement_reduction = early_retirement_reduction
			record.benefit = benefit
			record.save()
		except Record.DoesNotExist:
			record = self.create(
				person=respondent,
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
		return record

	# assumes that record is pre created 
	def calculate_dependent_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record):
		beneficiary_record.spousal_insurance_benefit = benefit_rules.spousal_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_basic_primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_beneficiary_basic_primary_insurance_amount,
			government_pension_offset=beneficiary_government_pension_offset) # seperate gpo if spousal insurance benefit before gpo is used somewhere else like basic pia
		beneficiary_record.save()
		return beneficiary_record

	# assumes that record is pre created
	def calculate_survivor_benefits(self, benefit_rules, respondent, beneficiary_record, spousal_beneficiary_record):
		beneficiary_record.survivor_insurance_benefit = benefit_rules.survivor_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=respondent.survivor_early_retirement_reduction, 
			spousal_delay_retirement_factor=spousal_beneficiary_delay_retirement_credit,
			government_pension_offset=beneficiary_government_pension_offset)
		beneficiary_record.save()
		return beneficiary_record

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