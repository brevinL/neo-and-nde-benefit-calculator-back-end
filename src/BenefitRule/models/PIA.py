from math import isinf, inf, floor
from django.db import models
from .BenefitRule import BenefitRule
from .Money import Money
from .Utilities import ordinal

# https://www.ssa.gov/oact/cola/piaformula.html
# https://www.ssa.gov/oact/cola/bendpoints.html
'''
For 2018 these portions are the first $895, the amount between $895 and $5,397, and the amount over $5,397. 
These dollar amounts are the "bend points" of the 2018 PIA formula. 
A table shows bend points, for years beginning with 1979, for both the PIA and maximum family benefit formulas.

bendpoints != portions
'''
class PrimaryInsuranceAmount(BenefitRule):
	WEP = 'W'
	BASIC = 'B'
	TYPE_OF_PRIMARY_INSURANCE_FORUMLA_CHOICES = (
		(WEP, "Windfall Elimination Provision's Primary Insurance Forumla"),
		(BASIC, 'Basic Primary Insurance Forumla')
	)
	type_of_primary_insurance_formula = models.CharField(
		max_length=1,
		choices=TYPE_OF_PRIMARY_INSURANCE_FORUMLA_CHOICES,
	)

	def calculate(self, average_indexed_monthly_earning, year_of_coverage):
		bendpoints = self.bendpoints.order_by('order')
		factors = self.factors.order_by('order')

		primary_insurance_amount = Money(amount=0)
		for index, factor in enumerate(factors):
			min_dollar = bendpoints[index].min_dollar_amount
			max_dollar = bendpoints[index].max_dollar_amount

			if isinf(min_dollar):
				min_dollar = Money(amount=0)
			elif isinf(max_dollar):
				max_dollar = Money(amount=0)

			primary_insurance_amount += max(Money(amount=0), factor.calculate(year_of_coverage) * (min(average_indexed_monthly_earning, max_dollar) - min_dollar))
			
		return floor(primary_insurance_amount * 10) / 10

class BendPoint(models.Model):
	min_dollar_amount = models.FloatField()
	max_dollar_amount = models.FloatField()
	order = models.IntegerField()
	primary_insurance_amount = models.ForeignKey(PrimaryInsuranceAmount, on_delete=models.CASCADE, related_name="bendpoints", null=True)

	class Meta:
		ordering  = ['order']

# https://www.ssa.gov/oact/cola/piaformula.html
# https://secure.ssa.gov/poms.nsf/lnx/0300605362
class Factor(models.Model):
	order = models.IntegerField()
	primary_insurance_amount = models.ForeignKey(PrimaryInsuranceAmount, on_delete=models.CASCADE, related_name="factors", null=True)

	def calculate(self, year_of_coverage):
		piece = self.factor_pieces.get(min_year_of_coverage__lte=year_of_coverage, max_year_of_coverage__gte=year_of_coverage)
		return piece.calculate(year_of_coverage)

class FactorPiece(models.Model):
	inital_factor = models.FloatField(default=0)
	# https://stackoverflow.com/questions/10539026/how-to-create-a-django-floatfield-with-maximum-and-minimum-limits
	min_year_of_coverage = models.FloatField(default=-inf)
	max_year_of_coverage = models.FloatField(default=inf)
	year_of_coverage_change = models.IntegerField(default=1)
	factor_change = models.FloatField(default=0)
	order = models.IntegerField()
	factor = models.ForeignKey(Factor, on_delete=models.CASCADE, related_name="factor_pieces", null=True)

	def calculate(self, year_of_coverage):
		if(not(self.min_year_of_coverage <= year_of_coverage and self.max_year_of_coverage >= year_of_coverage)):
			raise ValueError(f'year_of_coverage: {year_of_coverage} is not with in range, min_year_of_coverage: {self.min_year_of_coverage}, max_year_of_coverage: {self.max_year_of_coverage}.')

		if(isinf(self.min_year_of_coverage) and not isinf(self.max_year_of_coverage)):
			return (self.inital_factor + (self.max_year_of_coverage - year_of_coverage) * ( self.factor_change / self.year_of_coverage_change )) 
		elif(not isinf(self.min_year_of_coverage)):
			return (self.inital_factor + (year_of_coverage - self.min_year_of_coverage) * ( self.factor_change / self.year_of_coverage_change )) 
		elif(self.factor_change / self.year_of_coverage_change == 0):
			return self.inital_factor 