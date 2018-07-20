from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import WindfallEliminationProvision, Money, ordinal, currency

class WindfallEliminationProvisionTestCase(TestCase):
	def setUp(self):
		WindfallEliminationProvision.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31))

	def test_calculate(self):
		years_of_non_covered_earnings = 25
		wep = WindfallEliminationProvision.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(427.80,
			wep.calculate(
				primary_insurance_amount=Money(amount=839), 
				wep_primary_insurance_amount=Money(amount=411.20),
				monthly_non_covered_pension=Money(amount=1595.24)
			))