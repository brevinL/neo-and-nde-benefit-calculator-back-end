from fractions import Fraction
from django.db import models
from BenefitRule.models import GovernmentPensionOffset
from .Instruction import Instruction

class GovernmentPensionOffset(GovernmentPensionOffset):
	class Meta:
		proxy = True

	def stepByStep(self, monthly_non_covered_pension):
		stepByStep = []

		stepByStep.append(Instruction('Get monthly non covered pension',
			[f'monthly non covered pension = {monthly_non_covered_pension}']))

		stepByStep.append(Instruction('Get offset',
			[f'offset = {Fraction(self.offset).limit_denominator()}']))

		stepByStep.append(Instruction('Multiply the monthly non covered pension with the offset',
			['government pension offset = monthly non covered pension x offset',
			f'government pension offset = {monthly_non_covered_pension} x {Fraction(self.offset).limit_denominator()}',
			f'government pension offset = {monthly_non_covered_pension * self.offset}']))

		return stepByStep