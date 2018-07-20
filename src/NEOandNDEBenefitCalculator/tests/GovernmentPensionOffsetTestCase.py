from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Money
from NEOandNDEBenefitCalculator.models import GovernmentPensionOffset, Instruction

class GovernmentPensionOffsetTestCase(TestCase):
	def setUp(self):
		GovernmentPensionOffset.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)

	def test_stepByStep(self):
		gpo = GovernmentPensionOffset.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		instructions = [
			Instruction(description='Get monthly non covered pension',
				expressions=['monthly non covered pension = $600.00']),
			Instruction(description='Get offset',
				expressions=['offset = 2/3']),
			Instruction(description='Multiply the monthly non covered pension with the offset',
				expressions=['government pension offset = monthly non covered pension x offset',
					'government pension offset = $600.00 x 2/3',
					'government pension offset = $400.00'])
		]

		self.assertEqual(instructions, gpo.stepByStep(monthly_non_covered_pension=Money(amount=600)))