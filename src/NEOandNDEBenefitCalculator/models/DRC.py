from math import isinf
from django.db import models
from BenefitRule.models import BenefitRule, percentage, DelayRetirementCredit
from .Instruction import Instruction

# https://www.ssa.gov/planners/retire/delayret.html
class DelayRetirementCredit(DelayRetirementCredit):
	class Meta:
		proxy = True

	def stepByStep(self, year_of_birth, normal_retirement_age, delayed_retirement_age):
		stepByStep = []

		normal_retirement_age = float(normal_retirement_age)
		delayed_retirement_age = float(delayed_retirement_age)
		
		stepByStep.append(Instruction('Get normal retirement age',
			[f'normal retirement age = {normal_retirement_age}']))

		stepByStep.append(Instruction('Get delayed retirement age',
			[f'delayed retirement age = {delayed_retirement_age}']))

		stepByStep.append(Instruction('Determine if person is eligible for delay retirement credit', 
				['normal retirement age < delayed retirement age?',
				f'{normal_retirement_age} < {delayed_retirement_age}?',
				f'{normal_retirement_age < delayed_retirement_age}']))

		if normal_retirement_age >= delayed_retirement_age:
			stepByStep.append(Instruction('Set delay retirement benefit percentage increase to zero', 
				[f'delay retirement benefit percentage increase = {percentage(0)}']))
			return stepByStep

		stepByStep.append(Instruction('Get delay retirement age limit',
			[f'delay retirement age limit = {self.age_limit}']))

		stepByStep.append(Instruction('Capped retirement age if retirement age is greater than delay retirement age limit',
			['retirement age = min(delay retirement age limit, retirement age)',
			f'retirement age = min({self.age_limit}, {delayed_retirement_age})',
			f'retirement age = {min(self.age_limit, delayed_retirement_age)}']))
		delayed_retirement_age = min(self.age_limit, delayed_retirement_age)

		number_of_years_delayed = delayed_retirement_age + 1 - normal_retirement_age
		stepByStep.append(Instruction('Determine number of years delayed',
			['number of years delayed = retirement age + 1 - normal retirement age'
			f'number of years delayed = {delayed_retirement_age} + 1 - {normal_retirement_age}',
			f'number of years delayed = {delayed_retirement_age + 1 - normal_retirement_age}']))

		forumla_piece = self.delay_retirement_credit_pieces.get(min_year__lte=year_of_birth, max_year__gte=year_of_birth)
		yearly_percent_rate_of_increase = forumla_piece.calculate(year_of_birth)
		delay_retirement_benefit_percentage_increase = (min(self.age_limit, delayed_retirement_age) + 1 - normal_retirement_age) * yearly_percent_rate_of_increase

		stepByStep.append(Instruction('Determine number of years delayed',
			[f'delay retirement benefit percentage increase = number of years delayed * monthly percent rate of increase',
			f'delay retirement benefit percentage increase = {number_of_years_delayed} * {percentage(yearly_percent_rate_of_increase)}',
			f'delay retirement benefit percentage increase = {percentage(delay_retirement_benefit_percentage_increase)}']))

		return stepByStep