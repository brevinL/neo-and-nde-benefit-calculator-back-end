from fractions import Fraction
from django.db import models
from .BenefitRule import BenefitRule

# https://www.ssa.gov/planners/retire/gpo.html

# The GPO reduces the amount of your Social Security spouse's, widow's, or widower's benefits 
# two-thirds of the amount of your government pension. 
# For example, if you receive a monthly civil service pension of $600, 
# two-thirds of that, or $400, must be used to offset your Social Security spouse's, 
# widow's, or widower's benefits. If you are eligible for a $500 spouse's benefit, 
# you will receive $100 per month from Social Security ($500 - $400 = $100).
class GovernmentPensionOffset(BenefitRule):
	offset = models.FloatField()

	def calculate(self, monthly_non_covered_pension):
		return monthly_non_covered_pension * self.offset