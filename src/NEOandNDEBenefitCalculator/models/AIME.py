from django.db import models
from BenefitRule.models import AverageIndexedMonthlyEarning, Money, Person
from .Instruction import Instruction

class AverageIndexedMonthlyEarning(AverageIndexedMonthlyEarning):
	class Meta:
		proxy = True

	def stepByStep(self, taxable_earnings):
		stepByStep = []

		stepByStep.append(Instruction('Get indexed yearly earnings', 
			[f'indexed yearly earnings = {", ".join([str(x) for x in taxable_earnings])}']))

		sorted_taxable_earnings = sorted(taxable_earnings)
		stepByStep.append(Instruction(f'Sort indexed yearly earnings in descending order', 
			[f'indexed yearly earnings = {", ".join([str(x) for x in sorted_taxable_earnings])}']))

		highest_indexed_earnings = sorted_taxable_earnings[:self.max_years_for_highest_indexed_earnings]
		stepByStep.append(Instruction(f'Get highest {self.max_years_for_highest_indexed_earnings} indexed yearly earnings', 
			[f'highest {self.max_years_for_highest_indexed_earnings} indexed yearly earnings = {", ".join([str(x) for x in highest_indexed_earnings])}']))

		average_indexed_yearly_earning = sum(highest_indexed_earnings) / self.max_years_for_highest_indexed_earnings
		stepByStep.append(Instruction('Get average indexed yearly earning', 
			[f'average indexed yearly earning = ' \
			f'sum of highest {self.max_years_for_highest_indexed_earnings} indexed yearly earnings ' \
			'/ number of highest indexed yearly earnings',
			f'average indexed yearly earning = {sum(highest_indexed_earnings)} / {self.max_years_for_highest_indexed_earnings}',
			f'average indexed yearly earning = {average_indexed_yearly_earning}']))

		stepByStep.append(Instruction('Divide average indexed yearly earning by 12', 
			['average indexed monthly earning = average indexed yearly earning / 12',
			f'average indexed monthly earning = {average_indexed_yearly_earning} / 12',
			f'average indexed monthly earning = {average_indexed_yearly_earning / 12}']))

		return stepByStep