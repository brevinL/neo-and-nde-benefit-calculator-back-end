from math import isinf, inf
from fractions import Fraction
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from BenefitRule.models import BenefitRule, RetirementAge, EarlyRetirementBenefitReduction, percentage
from .Instruction import Instruction

class EarlyRetirementBenefitReduction(EarlyRetirementBenefitReduction):
	class Meta:
		proxy = True

	def stepByStep(self, normal_retirement_age, early_retirement_age):
		stepByStep = []

		stepByStep.append(Instruction('Get normal retirement age',
			[f'normal retirement age = {normal_retirement_age}']))

		stepByStep.append(Instruction('Get early retirement age',
			[f'early retirement age = {early_retirement_age}']))

		stepByStep.append(Instruction('Determine if person is eligible for early retirement benefit reduction', 
				['normal retirement age > early retirement age?',
				f'{normal_retirement_age} > {early_retirement_age}?',
				f'{normal_retirement_age > early_retirement_age}']))

		if normal_retirement_age <= early_retirement_age:
			stepByStep.append(Instruction('Set early retirement benefit percentage reduction to zero', 
				[f'early retirement benefit percentage reduction = {percentage(0)}']))
			return stepByStep

		stepByStep.append(Instruction('Determine number of months before normal retirement age', 
			['number of months before normal retirement age = | early retirement age - normal retirement age | * 12',
			f'number of months before normal retirement age = | {early_retirement_age} - {normal_retirement_age} | * 12',
			f'number of months before normal retirement age = {abs(early_retirement_age - normal_retirement_age)} * 12',
			f'number of months before normal retirement age = {abs(early_retirement_age - normal_retirement_age) * 12}']))

		difference_in_months = abs(early_retirement_age - normal_retirement_age) * 12

		stepByStep.append(Instruction('Set early retirement benefit percentage reduction to zero', 
			[f'early retirement benefit percentage reduction = {percentage(0)}']))

		benefit_reduction_factor = 0

		if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
			pieces = self.early_retirement_benefit_reduction_piece_set.all()
		elif self.benefit_type == self.SURVIVOR:
			pieces = self.survivor_early_retirement_benefit_reduction_piece_set.all()

		for piece in pieces:
			if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
				stepByStep.append(Instruction('For each month ' + 
					(f'(up to {piece.theshold_in_months} months) ' if not isinf(piece.theshold_in_months) else '') + 
					'before normal retirement age, ' \
					f'add {Fraction(piece.factor).limit_denominator()} of {percentage(piece.percentage)} to early retirement benefit percentage reduction', 
					['early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
					f'min(number of months before normal retirement age, ' + ('infinity' if isinf(piece.theshold_in_months) else str(piece.theshold_in_months)) + ') x ' \
					f'{Fraction(piece.factor).limit_denominator()} of {percentage(piece.percentage)}',
					f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor)} + ' \
					f'min({difference_in_months}, ' + ('infinity' if isinf(piece.theshold_in_months) else str(piece.theshold_in_months)) + ') x ' \
					f'{Fraction(piece.factor).limit_denominator()} x {percentage(piece.percentage)}',
					f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor)} + ' \
					f'{min(difference_in_months, piece.theshold_in_months)} x ' \
					f'{Fraction(piece.factor).limit_denominator()} x {percentage(piece.percentage)}',
					f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor + min(difference_in_months, piece.theshold_in_months) * piece.factor * piece.percentage)}']))
				benefit_reduction_factor += piece.calculate(difference_in_months)
				if difference_in_months - piece.theshold_in_months > 0:
					stepByStep.append(Instruction('Update number of months before normal retirement age', 
					[f'number of months before normal retirement age = {difference_in_months} - ' + ('infinity' if isinf(piece.theshold_in_months) else str(piece.theshold_in_months)),
					f'number of months before normal retirement age = {difference_in_months - piece.theshold_in_months}']))
				difference_in_months -= piece.theshold_in_months
			if self.benefit_type == self.SURVIVOR:
				stepByStep.append(Instruction('For each month before normal retirement age, ' \
					f'add {percentage(piece.factor)} to early retirement benefit percentage reduction', 
					['early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
					f'number of months before normal retirement age x {percentage(piece.factor)}',
					f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor)} + ' \
					f'{difference_in_months} x {percentage(piece.factor)}',
					f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor + difference_in_months * piece.factor)}']))
				benefit_reduction_factor += piece.factor
		return stepByStep
