from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import RetirementAge, EarlyRetirementBenefitReduction, Money, ordinal, currency

class EarlyRetirementBenefitReductionTestCase(TestCase):
	def setUp(self):
		nra = RetirementAge.objects.create(start_date=date.min, end_date=date.max, 
			retirement_type=RetirementAge.NORMAL)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=-inf, end_year=1937, 
			normal_retirement_age_change=0, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1937, end_year=1943, 
			normal_retirement_age_change=2/12, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1943, end_year=1954, 
			normal_retirement_age_change=0, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1954, end_year=1960, 
			normal_retirement_age_change=2/12, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1960, end_year=inf, 
			normal_retirement_age_change=0, year_of_birth_change=1)

		era = RetirementAge.objects.create(start_date=date.min, end_date=date.max, 
			retirement_type=RetirementAge.EARLIEST)
		era.retirement_age_pieces.create(initial_retirement_age=62, start_year=-inf, end_year=inf, 
			normal_retirement_age_change=0, year_of_birth_change=1)

		err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.PRIMARY)
		err.early_retirement_benefit_reduction_piece_set.create(factor=5/9, percentage=0.01, theshold_in_months=36)
		err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=inf)

		spousal_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.SPOUSAL)
		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=25/36, percentage=0.01, theshold_in_months=36)
		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=inf)

		survivor_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.SURVIVOR)
		survivor_err.survivor_early_retirement_benefit_reduction_piece_set.create(max_percentage_reduction=0.285)

	def test_calculate_early_retirement_benefit_reduction(self):
		err = EarlyRetirementBenefitReduction.objects.get(
			Q(benefit_type=EarlyRetirementBenefitReduction.PRIMARY) &
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0.25, err.calculate(normal_retirement_age=66, early_retirement_age=62))

	def test_calculate_early_retirement_benefit_reduction_is_not_eligible(self):
		err = EarlyRetirementBenefitReduction.objects.get(
			Q(benefit_type=EarlyRetirementBenefitReduction.PRIMARY) &
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0, err.calculate(normal_retirement_age=66, early_retirement_age=66))
		self.assertAlmostEqual(0, err.calculate(normal_retirement_age=66, early_retirement_age=67))

	def test_calcuate_early_retirement_benefit_reduction_for_spousal(self):
		spousal_err = EarlyRetirementBenefitReduction.objects.get(
			Q(benefit_type=EarlyRetirementBenefitReduction.SPOUSAL) & 
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0.30, spousal_err.calculate(normal_retirement_age=66, early_retirement_age=62))

	def test_calcuate_early_retirement_benefit_reduction_for_survivor(self):
		survivor_err = EarlyRetirementBenefitReduction.objects.get(
			Q(benefit_type=EarlyRetirementBenefitReduction.SURVIVOR) & 
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0.285, survivor_err.calculate(normal_retirement_age=66, early_retirement_age=62))