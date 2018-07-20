from django.db import models
from .BenefitRule import BenefitRule
from .ERR import EarlyRetirementBenefitReduction
from .Money import Money 

# https://www.ssa.gov/planners/retire/applying6.html
# https://www.ssa.gov/oact/quickcalc/spouse.html
# https://www.ssa.gov/OP_Home%2Fhandbook/handbook.03/handbook-0305.html
class SurvivorInsuranceBenefit(BenefitRule):
	max_benefit_entitlement_factor = models.FloatField()

	def maxEntitlement(self, spousal_primary_insurance_amount):
		return spousal_primary_insurance_amount * self.max_benefit_entitlement_factor

	# check(?) if spouse is deceased
	def calculate(self, primary_insurance_amount, deceased_spousal_primary_insurance_amount, 
		survivor_early_retirement_reduction_factor, spousal_delay_retirement_factor, government_pension_offset):
		max_entitlement = self.maxEntitlement(deceased_spousal_primary_insurance_amount)
		entitlement = max(max_entitlement,  deceased_spousal_primary_insurance_amount * (1-survivor_early_retirement_reduction_factor) + spousal_delay_retirement_factor)
		return max(Money(amount=0), entitlement - primary_insurance_amount - government_pension_offset) # test: never go negative