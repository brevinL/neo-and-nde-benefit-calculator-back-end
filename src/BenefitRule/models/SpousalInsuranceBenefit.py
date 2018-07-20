from fractions import Fraction
from django.db import models
from .BenefitRule import BenefitRule
from .ERR import EarlyRetirementBenefitReduction
from .Earning import Earning, Money

# https://www.ssa.gov/planners/retire/applying6.html
# https://www.ssa.gov/oact/quickcalc/spouse.html
# https://www.ssa.gov/OP_Home%2Fhandbook/handbook.03/handbook-0305.html
class SpousalInsuranceBenefit(BenefitRule):
	max_benefit_entitlement_factor = models.FloatField()

	# how to check if they applied for their own benefits?
	# case: applied but resulted in 0 due to wep cut vs didnt applied
	def isEntitled(self, primary_insurance_amount, spousal_primary_insurance_amount):
		return primary_insurance_amount < self.maxEntitlement(spousal_primary_insurance_amount)

	def maxEntitlement(self, spousal_primary_insurance_amount):
		return spousal_primary_insurance_amount * self.max_benefit_entitlement_factor

	# If a spouse is eligible for a retirement benefit based on his or her own earnings, 
	# and if that benefit is higher than the spousal benefit, 
	# then we pay the retirement benefit. Otherwise we pay the spousal benefit.
	def calculate(self, primary_insurance_amount, spousal_primary_insurance_amount, government_pension_offset):
		if(self.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount)): # test against money of 0 not 0
			return max(Money(amount=0), self.maxEntitlement(spousal_primary_insurance_amount) - primary_insurance_amount - government_pension_offset)
		else: # to be tested
			return Money(amount=0)