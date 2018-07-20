from math import isinf
from django.db import models
from .BenefitRule import BenefitRule
from .Utilities import percentage

# https://www.ssa.gov/planners/retire/delayret.html
class DelayRetirementCredit(BenefitRule):
	age_limit = models.IntegerField()

	def calculate(self, year_of_birth, normal_retirement_age, delayed_retirement_age):
		if normal_retirement_age >= delayed_retirement_age:
			return 0
		forumla_piece = self.delay_retirement_credit_pieces.get(min_year__lte=year_of_birth, max_year__gte=year_of_birth)
		yearly_percent_rate_of_increase = forumla_piece.calculate(year_of_birth)
		return (min(self.age_limit, delayed_retirement_age) + 1 - normal_retirement_age) * yearly_percent_rate_of_increase

class DelayRetirementCreditPiece(models.Model):
	inital_percentage = models.FloatField()
	min_year = models.FloatField()
	max_year = models.FloatField()
	percentage_rate = models.FloatField()
	year_change = models.IntegerField()
	delay_retirement_credit = models.ForeignKey(DelayRetirementCredit, 
		on_delete=models.CASCADE, related_name="delay_retirement_credit_pieces", null=True)

	def calculate(self, year_of_birth):
		if(not(self.min_year <= year_of_birth and self.max_year >= year_of_birth)):
			raise ValueError(f'year_of_birth: {year_of_birth} is not with in range, min_year: {self.min_year}, max_year: {self.max_year}.')

		if(isinf(self.min_year) and not isinf(self.max_year)):
			return self.inital_percentage + (self.max_year - year_of_birth) * ( self.percentage_rate / self.year_change )
		elif(not isinf(self.min_year)):
			return self.inital_percentage + (year_of_birth - self.min_year) * ( self.percentage_rate / self.year_change ) 
		elif(self.percentage_rate / self.year_change == 0):
			return self.inital_percentage 