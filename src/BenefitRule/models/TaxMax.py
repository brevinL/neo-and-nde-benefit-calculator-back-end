from django.db import models
from .BenefitRule import BenefitRule
from .Earning import Earning
from .Money import Money

# https://www.ssa.gov/planners/maxtax.html
class MaximumTaxableEarning(BenefitRule): # should be foregin key to money to get the decimal amount
	# amount = models.IntegerField()
	max_money = models.ForeignKey(Money, on_delete=models.CASCADE)

	def calculate(self, earning):
		return min(earning.money, self.max_money) # should it be returning earning to be consistent?