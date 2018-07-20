from math import isinf, floor
from BenefitRule.models import BenefitRule, PrimaryInsuranceAmount, Money
from .Instruction import Instruction

class PrimaryInsuranceAmount(PrimaryInsuranceAmount):
	class Meta:
		proxy = True

	def stepByStep(self, average_indexed_monthly_earning, year_of_coverage):
		stepByStep = []

		stepByStep.append(Instruction(f'Get average indexed monthly earning', 
			[f'average indexed monthly earning = {average_indexed_monthly_earning}']))

		bendpoints = self.bendpoints.order_by('order')
		factors = self.factors.order_by('order')

		primary_insurance_amount = Money(amount=0)
		stepByStep.append(Instruction(f'Initalize total primary insurance amount to 0', 
			[f'primary insurance amount = {primary_insurance_amount}']))

		for index, factor in enumerate(factors):
			min_dollar = Money(amount=bendpoints[index].min_dollar_amount)
			max_dollar = Money(amount=bendpoints[index].max_dollar_amount)

			if isinf(min_dollar.amount) and not isinf(max_dollar.amount):
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent his/her ' \
					f'average indexed monthly earning up to {max_dollar} to ' \
					f'total primary insurance amount'
			elif not isinf(min_dollar.amount) and isinf(max_dollar.amount):
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent his/her ' \
					f'average indexed monthly earning above {min_dollar} to ' \
					f'total primary insurance amount'
			elif not (isinf(min_dollar.amount) and isinf(max_dollar.amount)):
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent his/her ' \
					f'average indexed monthly earning between {min_dollar} and ' \
					f'{max_dollar} to total primary insurance amount'
			elif isinf(min_dollar.amount) and isinf(max_dollar.amount):
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent of all his/her ' \
					f'average indexed monthly earning to total primary insurance amount'
			else:
				description = ''

			if isinf(min_dollar.amount):
				min_dollar = Money(amount=0)
			elif isinf(max_dollar.amount):
				max_dollar = Money(amount=0)

			expressions = []
			expressions.append(f'primary insurance amount = ' \
				f'primary insurance amount + ' \
				f'max($0.00, factor x ( min(average indexed monthly earning, ' \
				'minimum dollar amount threshold) - maximum dollar amount threshold ))')
			expressions.append(f'primary insurance amount = max($0.00, {primary_insurance_amount} + ' \
				f'{factor.calculate(year_of_coverage)} x ' \
				f'( min({average_indexed_monthly_earning}, {max_dollar}) - {min_dollar} ))')

			primary_insurance_amount += max(0, factor.calculate(year_of_coverage) * (min(average_indexed_monthly_earning, max_dollar.amount) - min_dollar.amount))
			expressions.append(f'primary insurance amount = {primary_insurance_amount}')

			stepByStep.append(Instruction(description, expressions))

		stepByStep.append(Instruction(f'Round total primary insurance amount to the next lower multiple of $0.10 ' \
			'if it is not already a multiple of $0.10', 
			[f'primary insurance amount = floor(primary insurance amount * 10) / 10', 
			f'primary insurance amount = floor({primary_insurance_amount} * 10) / 10', 
			f'primary insurance amount = {floor(primary_insurance_amount * 10) / 10}']))
		
		return stepByStep