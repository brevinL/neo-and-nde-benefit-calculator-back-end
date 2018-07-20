from django.db import models
from .BenefitRule import BenefitRule
from .Earning import Earning

# https://www.ssa.gov/planners/maxtax.html
class MaximumTaxableEarning(BenefitRule):
	amount = models.IntegerField()

	def calculate(self, earning):
		return min(earning.money, self.amount)  