from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Person, Money
from NEOandNDEBenefitCalculator.models import SpousalInsuranceBenefit, Instruction

# need to create test for negative spousal benefit
class SpousalInsuranceBenefitTestCase(TestCase):
	def setUp(self):
		Person.objects.create(id=1, year_of_birth=1954)
		Person.objects.create(id=2, year_of_birth=1954)
		SpousalInsuranceBenefit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_benefit_entitlement_factor=1/2)

	def test_stepByStep_is_not_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		instructions = [
			Instruction(description='Get spousal\' primary insurance amount',
				expressions=['spousal\'s primary insurance amount = $1,829.00']),
			Instruction(description='Calculate the maximum entitlement to spousal insurance benefit',
				expressions=['maximum benefit entitlement = spousal\'s primary insurance amount x maximum benefit entitlement factor',
					'maximum benefit entitlement = $1,829.00 x 1/2',
					'maximum benefit entitlement = $914.50']),
			Instruction(description='Get primary insurance amount',
				expressions=['primary insurance amount = $1,000.00']),
			Instruction(description='Determine if person is entitled to spousal insurance benefit', 
				expressions=['primary insurance amount < maximum benefit entitlement?',
					'$1,000.00 < $914.50?',
					'False']),
			Instruction(description='Set spousal insurance benefit to zero',
				expressions=['spousal insurance benefit = $0.00'])
		]
		self.assertEqual(instructions, spousal_insurance_benefit.stepByStep(
			primary_insurance_amount=Money(amount=1000), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=213)))

	def test_stepByStep_is_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		instructions = [
			Instruction(description='Get spousal\' primary insurance amount',
				expressions=['spousal\'s primary insurance amount = $1,829.00']),
			Instruction(description='Calculate the maximum entitlement to spousal insurance benefit',
				expressions=['maximum benefit entitlement = spousal\'s primary insurance amount x maximum benefit entitlement factor',
					'maximum benefit entitlement = $1,829.00 x 1/2',
					'maximum benefit entitlement = $914.50']),
			Instruction(description='Get primary insurance amount',
				expressions=['primary insurance amount = $679.00']),
			Instruction(description='Determine if person is entitled to spousal insurance benefit', 
				expressions=['primary insurance amount < maximum benefit entitlement?',
					'$679.00 < $914.50?',
					'True']),
			Instruction(description='Set spousal insurance benefit to maximum benefit entitlement',
				expressions=['spousal insurance benefit = maximum benefit entitlement',
					'spousal insurance benefit = $914.50']),
			Instruction(description='Subtract the primary insurance amount from spousal insurance benefit',
				expressions=['spousal insurance benefit = spousal insurance benefit - primary insurance amount',
					f'spousal insurance benefit = $914.50 - $679.00',
					f'spousal insurance benefit = $235.50']),
			Instruction(description='Get government pension offset',
				expressions=[f'government pension offset = $213.00']),
			Instruction(description='Subtract the government pension offset from spousal insurance benefit',
				expressions=['spousal insurance benefit = spousal insurance benefit - government pension offset',
					f'spousal insurance benefit = $235.50 - $213.00',
					f'spousal insurance benefit = $22.50']),
			Instruction('Cap spousal insurance benefit',
				['spousal insurance benefit = max($0.00, spousal insurance benefit)',
				'spousal insurance benefit = max($0.00, $22.50)',
				'spousal insurance benefit = $22.50'])
		]
		self.assertEqual(instructions, spousal_insurance_benefit.stepByStep(
			primary_insurance_amount=Money(amount=679), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=213)))