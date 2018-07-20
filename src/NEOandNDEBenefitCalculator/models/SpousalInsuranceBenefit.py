from fractions import Fraction
from django.db import models
from BenefitRule.models import SpousalInsuranceBenefit, Money
from .Instruction import Instruction

class SpousalInsuranceBenefit(SpousalInsuranceBenefit):
	class Meta:
		proxy = True

	def stepByStep(self, primary_insurance_amount, spousal_primary_insurance_amount, government_pension_offset):
		stepByStep = []

		stepByStep.append(Instruction('Get spousal\' primary insurance amount',
			[f'spousal\'s primary insurance amount = {spousal_primary_insurance_amount}']))

		stepByStep.append(Instruction('Calculate the maximum entitlement to spousal insurance benefit',
			['maximum benefit entitlement = spousal\'s primary insurance amount x maximum benefit entitlement factor',
			f'maximum benefit entitlement = {spousal_primary_insurance_amount} x {Fraction(self.max_benefit_entitlement_factor).limit_denominator()}',
			f'maximum benefit entitlement = {spousal_primary_insurance_amount * self.max_benefit_entitlement_factor}']))

		stepByStep.append(Instruction('Get primary insurance amount',
			[f'primary insurance amount = {primary_insurance_amount}']))

		stepByStep.append(Instruction('Determine if person is entitled to spousal insurance benefit', 
			['primary insurance amount < maximum benefit entitlement?',
			f'{primary_insurance_amount} < {self.maxEntitlement(spousal_primary_insurance_amount)}?',
			f'{primary_insurance_amount < self.maxEntitlement(spousal_primary_insurance_amount)}']))

		if(not self.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount)):
			stepByStep.append(Instruction('Set spousal insurance benefit to zero',
				[f'spousal insurance benefit = {Money(amount=0)}']))
			return stepByStep

		spousal_insurance_benefit = self.maxEntitlement(spousal_primary_insurance_amount)

		stepByStep.append(Instruction('Set spousal insurance benefit to maximum benefit entitlement',
			['spousal insurance benefit = maximum benefit entitlement',
			f'spousal insurance benefit = {spousal_insurance_benefit}']))
		
		stepByStep.append(Instruction('Subtract the primary insurance amount from spousal insurance benefit',
				['spousal insurance benefit = spousal insurance benefit - primary insurance amount',
				f'spousal insurance benefit = {spousal_insurance_benefit} - {primary_insurance_amount}',
				f'spousal insurance benefit = {spousal_insurance_benefit - primary_insurance_amount}']))

		spousal_insurance_benefit -= primary_insurance_amount

		stepByStep.append(Instruction('Get government pension offset',
			[f'government pension offset = {government_pension_offset}']))

		stepByStep.append(Instruction('Subtract the government pension offset from spousal insurance benefit',
			['spousal insurance benefit = spousal insurance benefit - government pension offset',
			f'spousal insurance benefit = {spousal_insurance_benefit} - {government_pension_offset}',
			f'spousal insurance benefit = {spousal_insurance_benefit - government_pension_offset}']))

		return stepByStep