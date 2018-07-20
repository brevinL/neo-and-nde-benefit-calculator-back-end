from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Person, BendPoint, Factor, FactorPiece, Money
from NEOandNDEBenefitCalculator.models import PrimaryInsuranceAmount, Instruction

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

	def test_stepByStep(self):
		pia = PrimaryInsuranceAmount.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31)),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
		)
		first_pia_factor = max(0, 0 + 0.9 * ( min(1071, 856) - 0 ))
		second_pia_factor = max(0, 0.32 * ( min(1071, 5157) - 856 ))
		third_pia_factor = max(0, 0.15 * ( min(1071, 0) - 5157 ))
		instructions = [
			Instruction(description='Get average indexed monthly earning', 
				expressions=['average indexed monthly earning = $1,071.00']),
			Instruction(description='Initalize total primary insurance amount to 0', 
				expressions=['primary insurance amount = $0.00']),
			Instruction(description='Add 90.0 percent his/her average indexed monthly ' \
					'earning up to $856.00 to total primary insurance amount', 
				expressions=['primary insurance amount = primary insurance amount + ' \
					'max($0.00, factor x ( min(average indexed monthly earning, minimum dollar amount threshold) - maximum dollar amount threshold ))',
					'primary insurance amount = max($0.00, $0.00 + 0.9 x ( min($1,071.00, $856.00) - $0.00 ))',
					'primary insurance amount = $770.40']),
			Instruction(description='Add 32.0 percent his/her average indexed monthly ' \
					'earning between $856.00 and $5,157.00 to total primary insurance amount', 
				expressions=['primary insurance amount = primary insurance amount + ' \
					'max($0.00, factor x ( min(average indexed monthly earning, minimum dollar amount threshold) - maximum dollar amount threshold ))',
					'primary insurance amount = max($0.00, $770.40 + 0.32 x ' \
					'( min($1,071.00, $5,157.00) - $856.00 ))',
					'primary insurance amount = $839.20']),
			Instruction(description='Add 15.0 percent his/her average indexed monthly ' \
					'earning above $5,157.00 to total primary insurance amount', 
				expressions=['primary insurance amount = primary insurance amount + ' \
					'max($0.00, factor x ( min(average indexed monthly earning, minimum dollar amount threshold) - maximum dollar amount threshold ))',
					'primary insurance amount = max($0.00, $839.20 + ' \
					'0.15 x ( min($1,071.00, $0.00) - $5,157.00 ))',
					'primary insurance amount = $839.20']),
			Instruction(description='Round total primary insurance amount to the next lower multiple of $0.10 ' \
					'if it is not already a multiple of $0.10', 
				expressions=['primary insurance amount = floor(primary insurance amount * 10) / 10', 
					'primary insurance amount = floor($839.20 * 10) / 10', 
					'primary insurance amount = $839.20'])
		]
		self.assertEqual(instructions, pia.stepByStep(
			average_indexed_monthly_earning=Money(amount=1071), 
			year_of_coverage=0))
