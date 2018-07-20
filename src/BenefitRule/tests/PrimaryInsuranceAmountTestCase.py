from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Person, PrimaryInsuranceAmount, BendPoint, Factor, FactorPiece, Money, ordinal, currency

class PrimaryInsuranceAmountTestCase(TestCase):
	def setUp(self):
		Person.objects.create(id=1, year_of_birth=1954)

		pia = PrimaryInsuranceAmount.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC)
		BendPoint.objects.create(min_dollar_amount=-inf, max_dollar_amount=856, order=1, primary_insurance_amount=pia)
		BendPoint.objects.create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=pia)
		BendPoint.objects.create(min_dollar_amount=5157, max_dollar_amount=inf, order=3, primary_insurance_amount=pia)

		f1 = Factor.objects.create(order=1, primary_insurance_amount=pia)
		FactorPiece.objects.create(inital_factor=0.90, order=1, factor=f1)

		f2 = Factor.objects.create(order=2, primary_insurance_amount=pia)
		FactorPiece.objects.create(inital_factor=0.32, order=1, factor=f2)

		f3 = Factor.objects.create(order=3, primary_insurance_amount=pia)
		FactorPiece.objects.create(inital_factor=0.15, order=1, factor=f3)

		wep_pia = PrimaryInsuranceAmount.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP)
		BendPoint.objects.create(min_dollar_amount=-inf, max_dollar_amount=856, order=1, primary_insurance_amount=wep_pia)
		BendPoint.objects.create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=wep_pia)
		BendPoint.objects.create(min_dollar_amount=5157, max_dollar_amount=inf, order=3, primary_insurance_amount=wep_pia)

		f1 = Factor.objects.create(order=1, primary_insurance_amount=wep_pia)
		FactorPiece.objects.create(inital_factor=0.40, min_year_of_coverage=-inf, max_year_of_coverage=20, order=1, factor=f1)
		FactorPiece.objects.create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2, factor=f1)
		FactorPiece.objects.create(inital_factor=0.90, min_year_of_coverage=30, max_year_of_coverage=inf, order=3, factor=f1)

		f2 = Factor.objects.create(order=2, primary_insurance_amount=wep_pia)
		FactorPiece.objects.create(inital_factor=0.32, order=1, factor=f2)

		f3 = Factor.objects.create(order=3, primary_insurance_amount=wep_pia)
		FactorPiece.objects.create(inital_factor=0.15, order=1, factor=f3)

	def test_calculate_normal_pia_within_parameter(self):
		pia = PrimaryInsuranceAmount.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31)),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
		)
		self.assertAlmostEqual(839.20, pia.calculate(average_indexed_monthly_earning=1071, year_of_coverage=0))

	def test_calculate_wep_pia_within_parameter(self):
		wep_pia = PrimaryInsuranceAmount.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31)),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP
		)
		self.assertAlmostEqual(411.20, wep_pia.calculate(average_indexed_monthly_earning=1071, year_of_coverage=15))

	def test_factors_order(self):
		pia = PrimaryInsuranceAmount.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31)),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
		)
		result = []
		for factor in pia.factors.all():
			result.append(factor.calculate(year_of_coverage=0))
		self.assertEqual([0.90, 0.32, 0.15], result)
