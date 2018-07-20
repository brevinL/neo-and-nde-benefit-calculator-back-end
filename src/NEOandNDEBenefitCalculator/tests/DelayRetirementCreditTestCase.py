from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import DelayRetirementCreditPiece, Money
from NEOandNDEBenefitCalculator.models import DelayRetirementCredit, Instruction

class DelayRetirementCreditTestCase(TestCase):
	def setUp(self):
		drc = DelayRetirementCredit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), age_limit=70)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.055, min_year=1933, max_year=1934, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.06, min_year=1935, max_year=1936, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.065, min_year=1937, max_year=1938, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.07, min_year=1939, max_year=1940, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.075, min_year=1941, max_year=1942, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.08, min_year=1943, max_year=inf, percentage_rate=0, year_change=1, delay_retirement_credit=drc)

	def test_stepByStep_no_pieces(self):
		drc = DelayRetirementCredit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), age_limit=70)
		with self.assertRaises(ObjectDoesNotExist):
			drc.stepByStep(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=80)

	def test_stepByStep_no_delay_retirement(self):
		drc = DelayRetirementCredit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		instructions = [
			Instruction(description='Get normal retirement age',
				expressions=['normal retirement age = 67']),
			Instruction(description='Get delayed retirement age',
				expressions=['delayed retirement age = 67']),
			Instruction(description='Determine if person is eligible for delay retirement credit', 
				expressions=['normal retirement age < delayed retirement age?',
					'67 < 67?',
					'False']),
			Instruction(description='Set delay retirement benefit percentage increase to zero',
				expressions=['delay retirement benefit percentage increase = 0.00%'])
		]
		self.assertEqual(instructions, drc.stepByStep(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=67))

	def test_stepByStep_with_delay_retirement(self):
		drc = DelayRetirementCredit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		instructions = [
			Instruction(description='Get normal retirement age',
				expressions=['normal retirement age = 67']),
			Instruction(description='Get delayed retirement age',
				expressions=['delayed retirement age = 80']),
			Instruction(description='Determine if person is eligible for delay retirement credit', 
				expressions=['normal retirement age < delayed retirement age?',
					'67 < 80?',
					'True']),
			Instruction('Get delay retirement age limit',
				['delay retirement age limit = 70']),
			Instruction('Capped retirement age if retirement age is greater than delay retirement age limit',
				['retirement age = min(delay retirement age limit, retirement age)',
				'retirement age = min(70, 80)',
				'retirement age = 70']),
			Instruction('Determine number of years delayed',
				['number of years delayed = retirement age + 1 - normal retirement age'
				'number of years delayed = 70 + 1 - 67',
				'number of years delayed = 4']),
			Instruction('Determine number of years delayed',
				['delay retirement benefit percentage increase = number of years delayed * monthly percent rate of increase',
				'delay retirement benefit percentage increase = 4 * 8.00%',
				'delay retirement benefit percentage increase = 32.00%'])
		]
		self.assertEqual(instructions, drc.stepByStep(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=80))
