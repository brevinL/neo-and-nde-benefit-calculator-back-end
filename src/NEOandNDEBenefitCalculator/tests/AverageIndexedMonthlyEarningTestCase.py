from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Person, Earning, Money, MaximumTaxableEarning
from NEOandNDEBenefitCalculator.models import AverageIndexedMonthlyEarning, Instruction

class AverageIndexedMonthlyEarningTestCase(TestCase):
	def setUp(self):
		Person.objects.create(id=1, year_of_birth=1954)
		AverageIndexedMonthlyEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_years_for_highest_indexed_earnings=35)

	def test_stepByStep(self):
		years_of_covered_earnings = 15
		taxable_earnings = []
		person = Person.objects.get(id=1)
		for i in range(0, years_of_covered_earnings):
			Earning.objects.create(money=Money.objects.create(amount=30000), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		maxtax = MaximumTaxableEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), amount=118500)
		for earning in person.earning_set.filter(type_of_earning=Earning.COVERED, time_period=Earning.YEARLY):
			taxable_earnings.append(maxtax.calculate(earning))
		aime = AverageIndexedMonthlyEarning.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31)))

		instructions = [
			Instruction(description='Get indexed yearly earnings',
				expressions=['indexed yearly earnings = ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00']),
			Instruction(description='Sort indexed yearly earnings in descending order', 
				expressions=['indexed yearly earnings = ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00']),
			Instruction(description='Get highest 35 indexed yearly earnings', 
				expressions=['highest 35 indexed yearly earnings = ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
				'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00']),
			Instruction(description='Get average indexed yearly earning', 
				expressions=[f'average indexed yearly earning = sum of highest 35 indexed yearly earnings ' \
				'/ number of highest indexed yearly earnings',
				'average indexed yearly earning = $450,000.00 / 35',
				'average indexed yearly earning = $12,857.14']),
			Instruction(description='Divide average indexed yearly earning by 12', 
				expressions=['average indexed monthly earning = average indexed yearly earning / 12',
				'average indexed monthly earning = $12,857.14 / 12',
				'average indexed monthly earning = $1,071.43'])
		]
		self.assertEqual(instructions, aime.stepByStep(taxable_earnings=taxable_earnings))