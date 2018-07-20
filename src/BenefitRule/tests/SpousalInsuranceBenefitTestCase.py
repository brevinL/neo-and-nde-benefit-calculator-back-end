from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Person, SpousalInsuranceBenefit, Money, ordinal, currency

class SpousalInsuranceBenefitTestCase(TestCase):
	def setUp(self):
		Person.objects.create(id=1, year_of_birth=1954)
		Person.objects.create(id=2, year_of_birth=1954)
		SpousalInsuranceBenefit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_benefit_entitlement_factor=1/2)

	def test_isEntitled_is_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		primary_insurance_amount = Money(amount=411)
		spousal_primary_insurance_amount = Money(amount=1829)
		self.assertTrue(spousal_insurance_benefit.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount))

	def test_isEntitled_is_not_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		primary_insurance_amount = Money(amount=1000)
		spousal_primary_insurance_amount = Money(amount=1829)
		self.assertFalse(spousal_insurance_benefit.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount))

	def test_maxEntitlement(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		spousal_primary_insurance_amount = Money(amount=1829)
		self.assertAlmostEqual(914.5, spousal_insurance_benefit.maxEntitlement(spousal_primary_insurance_amount))

	def test_calculate_is_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(22.50, spousal_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=679), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=213)))

		self.assertAlmostEqual(0, spousal_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=411), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=1064)))

	def test_calculate_is_not_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0, spousal_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=411), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=1064)))