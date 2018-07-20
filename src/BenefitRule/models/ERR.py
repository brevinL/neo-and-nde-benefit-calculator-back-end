from math import isinf, inf
from fractions import Fraction
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from .BenefitRule import BenefitRule
from .RA import RetirementAge
from .Utilities import percentage

# https://www.ssa.gov/oact/quickcalc/early_late.html
# https://www.ssa.gov/oact/quickcalc/earlyretire.html
# https://www.ssa.gov/oact/quickcalc/spouse.html
# https://www.ssa.gov/OP_Home%2Fhandbook/handbook.07/handbook-0724.html
'''
A spousal benefit is reduced 25/36 of 1% for each month before normal retirement age, up to 36 months. 
If the number of months exceeds 36, then the benefit is further reduced 5/12 of 1% per month.
'''
class EarlyRetirementBenefitReduction(BenefitRule):
	SPOUSAL = 'SP'
	PRIMARY = 'PR'
	SURVIVOR = 'SU'
	BENEFIT_TYPE_CHOICES = (
		(SPOUSAL, 'Spousal'),
		(PRIMARY, 'Primary'),
		(SURVIVOR, 'Survivor')
	)
	benefit_type = models.CharField(
		max_length=2,
		choices=BENEFIT_TYPE_CHOICES,
		default=PRIMARY,
	)

	def calculate(self, normal_retirement_age, early_retirement_age):
		if normal_retirement_age <= early_retirement_age:
			return 0
		difference_in_months = abs(early_retirement_age - normal_retirement_age) * 12
		benefit_reduction_factor = 0

		if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
			pieces = self.early_retirement_benefit_reduction_piece_set.all()
		elif self.benefit_type == self.SURVIVOR:
			pieces = self.survivor_early_retirement_benefit_reduction_piece_set.all()

		for piece in pieces:
			benefit_reduction_factor += piece.calculate(difference_in_months)
			if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
				difference_in_months -= piece.theshold_in_months

		return benefit_reduction_factor

# critical to explain how the factors are created by writing a stepbystep in the pieces
class EarlyRetirementBenefitReductionPiece(models.Model):
	factor = models.FloatField()
	percentage = models.FloatField()
	theshold_in_months = models.FloatField(validators=[MinValueValidator(0)], default=inf)
	early_retirement_benefit_reduction = models.ForeignKey(EarlyRetirementBenefitReduction, 
		on_delete=models.CASCADE, related_name="early_retirement_benefit_reduction_piece_set")

	def calculate(self, months):
		return self.factor * self.percentage * min(self.theshold_in_months, months)

class SurvivorEarlyRetirementBenefitReductionPiece(models.Model):
	max_percentage_reduction = models.FloatField()
	# while time is infinite, retirement age (theshold_in_months) is bound to the finite life span of a human
	early_retirement_benefit_reduction = models.ForeignKey(EarlyRetirementBenefitReduction, 
		on_delete=models.CASCADE, related_name="survivor_early_retirement_benefit_reduction_piece_set")
	
	@property
	def factor(self):
		normal_retirement_age = RetirementAge.objects.get(
			Q(retirement_type=RetirementAge.NORMAL) &
			Q(start_date__lte=self.early_retirement_benefit_reduction.start_date) & 
			Q(end_date__gte=self.early_retirement_benefit_reduction.end_date)
		).calculate(self.early_retirement_benefit_reduction.start_date.year)
		earliest_retirement_age = RetirementAge.objects.get(
			Q(retirement_type=RetirementAge.EARLIEST) &
			Q(start_date__lte=self.early_retirement_benefit_reduction.start_date) & 
			Q(end_date__gte=self.early_retirement_benefit_reduction.end_date)
		).calculate(self.early_retirement_benefit_reduction.start_date.year)
		return self.max_percentage_reduction / (abs(normal_retirement_age - earliest_retirement_age + 1) * 12)

	# assumes that months is the full retirement (i.e. 62 to 66) when it shouldn't
	def calculate(self, months):
		return self.factor * months