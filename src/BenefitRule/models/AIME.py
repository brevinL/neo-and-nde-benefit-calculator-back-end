from django.db import models
from .BenefitRule import BenefitRule
from .Money import Money
from .Utilities import ordinal

# https://www.ssa.gov/oact/cola/Benefits.html
# https://www.ssa.gov/oact/progdata/retirebenefit1.html
class AverageIndexedMonthlyEarning(BenefitRule):
	max_years_for_highest_indexed_earnings = models.IntegerField()

	# https://obliviousinvestor.com/how-social-security-benefits-are-calculated/
	def calculate(self, taxable_earnings): # test against []
		if not taxable_earnings:
			return Money(amount=0)
		highest_indexed_earnings = sorted(taxable_earnings, reverse=True)[:self.max_years_for_highest_indexed_earnings]
		average_indexed_yearly_earning = sum(highest_indexed_earnings) / self.max_years_for_highest_indexed_earnings
		average_indexed_monthly_earning = average_indexed_yearly_earning / 12
		return average_indexed_monthly_earning