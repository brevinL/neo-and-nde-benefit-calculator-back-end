from django.db import models
from BenefitRule.models import RetirementAge, Money, Person
from .Instruction import Instruction

class RetirementAge(RetirementAge):
	class Meta:
		proxy = True

	def stepByStep(self, taxable_earnings):
		return []