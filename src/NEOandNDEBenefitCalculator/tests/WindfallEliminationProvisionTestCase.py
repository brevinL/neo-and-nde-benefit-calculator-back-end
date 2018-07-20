from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Money
from NEOandNDEBenefitCalculator.models import WindfallEliminationProvision, Instruction

class WindfallEliminationProvisionTestCase(TestCase):
	def setUp(self):
		WindfallEliminationProvision.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31))

	def test_stepByStep(self):
		years_of_non_covered_earnings = 25
		wep = WindfallEliminationProvision.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31)))
		instructions = [
			Instruction(description="Get WEP's primary insurance amount",
				expressions=["WEP's primary insurance amount = primary insurance amount",
					"WEP's primary insurance amount = $411.20"]),
			Instruction(description="Get monthly non covered pension",
				expressions=["monthly non covered pension = $1,595.24"]),
			Instruction(description="Get primary insurance amount",
				expressions=["primary insurance amount = $839.00"]),
			Instruction(description='Find Windfall Elimination Provision reduction', 
				expressions=['WEP reduction = min(monthly non covered pension x 1/2, max(primary insurance amount - WEP\'s primary insurance amount, 0))',
					'WEP reduction = min($1,595.24 x 1/2, max($839.00 - $411.20, 0))',
					'WEP reduction = min($797.62, max($427.80, 0)',
					'WEP reduction = min($797.62, $427.80)',
					'WEP reduction = $427.80'])
		]
		self.assertEqual(instructions, wep.stepByStep(
			primary_insurance_amount=Money(amount=839), 
			wep_primary_insurance_amount=Money(amount=411.20),
			monthly_non_covered_pension=Money(amount=1595.24)
		))