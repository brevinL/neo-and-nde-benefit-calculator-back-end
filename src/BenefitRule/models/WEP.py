from django.db import models
from .BenefitRule import BenefitRule
from .Money import Money

# https://secure.ssa.gov/poms.nsf/lnx/0300605362
# https://www.ssa.gov/planners/retire/wep-chart.html
# https://www.ssa.gov/planners/retire/anyPiaWepjs04.html
'''
The Windfall Elimination Provision (WEP) reduces your Eligibility Year (ELY) benefit amount 
before it is reduced or increased due to early retirement, delayed retirement credits, 
cost-of-living adjustments (COLA), or other factors.
'''
class WindfallEliminationProvision(BenefitRule):
	# why not have pia as a parameter rather than a one to one?
	def calculate(self, primary_insurance_amount, wep_primary_insurance_amount, monthly_non_covered_pension):
		# the total WEP reduction is limited to one-half of the pension based on the earnings that were not covered by Social Security
		return min(monthly_non_covered_pension * 1/2, primary_insurance_amount - wep_primary_insurance_amount)