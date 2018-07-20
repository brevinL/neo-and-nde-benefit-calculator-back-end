from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import GovernmentPensionOffset, Money, ordinal, currency

class GovernmentPensionOffsetTestCase(TestCase):
	def setUp(self):
		GovernmentPensionOffset.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)

	def test_calculate(self):
		gpo = GovernmentPensionOffset.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(600 * 2/3, gpo.calculate(monthly_non_covered_pension=Money(amount=600)))