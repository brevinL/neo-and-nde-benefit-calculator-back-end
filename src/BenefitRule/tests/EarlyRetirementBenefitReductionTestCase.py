from datetime import date
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import RetirementAge, EarlyRetirementBenefitReduction, MIN_POSITIVE_INTEGER, MAX_POSITIVE_INTEGER, MIN_INTEGER, MAX_INTEGER

class EarlyRetirementBenefitReductionTestCase(TestCase):
	def setUp(self):
		err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.PRIMARY)
		err.early_retirement_benefit_reduction_piece_set.create(factor=5/9, percentage=0.01, theshold_in_months=36)
		err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=MAX_POSITIVE_INTEGER)

		spousal_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.SPOUSAL)
		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=25/36, percentage=0.01, theshold_in_months=36)
		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=MAX_POSITIVE_INTEGER)

		survivor_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.SURVIVOR)
		survivor_err.survivor_early_retirement_benefit_reduction_piece_set.create(max_percentage_reduction=0.285)

	def test_calculate_early_retirement_benefit_reduction(self):
		err = EarlyRetirementBenefitReduction.objects.get(
			benefit_type=EarlyRetirementBenefitReduction.PRIMARY,
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(0.25, err.calculate(normal_retirement_age=66, early_retirement_age=62))

	def test_calculate_early_retirement_benefit_reduction_is_not_eligible(self):
		err = EarlyRetirementBenefitReduction.objects.get(
			benefit_type=EarlyRetirementBenefitReduction.PRIMARY,
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(0, err.calculate(normal_retirement_age=66, early_retirement_age=66))
		self.assertAlmostEqual(0, err.calculate(normal_retirement_age=66, early_retirement_age=67))

	def test_calcuate_early_retirement_benefit_reduction_for_spousal(self):
		spousal_err = EarlyRetirementBenefitReduction.objects.get(
			benefit_type=EarlyRetirementBenefitReduction.SPOUSAL,
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(0.30, spousal_err.calculate(normal_retirement_age=66, early_retirement_age=62))

	def test_calcuate_early_retirement_benefit_reduction_for_survivor(self):
		nra = RetirementAge.objects.create(start_date=date.min, end_date=date.max, 
			retirement_type=RetirementAge.NORMAL)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=MIN_INTEGER, end_year=1937, 
			normal_retirement_age_change=0, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1937, end_year=1943, 
			normal_retirement_age_change=2/12, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1943, end_year=1954, 
			normal_retirement_age_change=0, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1954, end_year=1960, 
			normal_retirement_age_change=2/12, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=1960, end_year=MAX_INTEGER, 
			normal_retirement_age_change=0, year_of_birth_change=1)

		era = RetirementAge.objects.create(start_date=date.min, end_date=date.max, 
			retirement_type=RetirementAge.EARLIEST)
		era.retirement_age_pieces.create(initial_retirement_age=62, start_year=MIN_INTEGER, end_year=MAX_INTEGER, 
			normal_retirement_age_change=0, year_of_birth_change=1)

		survivor_err = EarlyRetirementBenefitReduction.objects.get(
			benefit_type=EarlyRetirementBenefitReduction.SURVIVOR,
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(0.285, survivor_err.calculate(normal_retirement_age=66, early_retirement_age=62))

	# def test_stepByStep_no_early_retirement(self):
	# 	err = EarlyRetirementBenefitReduction.objects.get(
	# 		Q(benefit_type=EarlyRetirementBenefitReduction.PRIMARY) & 
	# 		Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
	# 	)
	# 	instructions = [
	# 		Instruction(description='Get normal retirement age',
	# 			expressions=['normal retirement age = 66']),
	# 		Instruction(description='Get early retirement age',
	# 			expressions=['early retirement age = 67']),
	# 		Instruction(description='Determine if person is eligible for early retirement benefit reduction', 
	# 			expressions=['normal retirement age > early retirement age?',
	# 				'66 > 67?',
	# 				'False']),
	# 		Instruction('Set early retirement benefit percentage reduction to zero', 
	# 			['early retirement benefit percentage reduction = 0.00%'])
	# 	]
	# 	self.assertEqual(instructions, err.stepByStep(normal_retirement_age=66, early_retirement_age=67))

	# def test_stepByStep_with_primary_early_retirement(self):
	# 	err = EarlyRetirementBenefitReduction.objects.get(
	# 		Q(benefit_type=EarlyRetirementBenefitReduction.PRIMARY) & 
	# 		Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
	# 	)
	# 	instructions = [
	# 		Instruction(description='Get normal retirement age',
	# 			expressions=['normal retirement age = 66']),
	# 		Instruction(description='Get early retirement age',
	# 			expressions=['early retirement age = 62']),
	# 		Instruction(description='Determine if person is eligible for early retirement benefit reduction', 
	# 			expressions=['normal retirement age > early retirement age?',
	# 				'66 > 62?',
	# 				'True']),
	# 		Instruction(description='Determine number of months before normal retirement age', 
	# 			expressions=['number of months before normal retirement age = | early retirement age - normal retirement age | * 12',
	# 			'number of months before normal retirement age = | 62 - 66 | * 12',
	# 			'number of months before normal retirement age = 4 * 12',
	# 			'number of months before normal retirement age = 48']),
	# 		Instruction('Set early retirement benefit percentage reduction to zero', 
	# 			['early retirement benefit percentage reduction = 0.00%']),
	# 		Instruction(description='For each month (up to 36.0 months) before normal retirement age, add 5/9 of 1.00% to ' \
	# 			'early retirement benefit percentage reduction', 
	# 			expressions=['early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
	# 			'min(number of months before normal retirement age, 36.0) x 5/9 of 1.00%',
	# 			'early retirement benefit percentage reduction = 0.00% + min(48, 36.0) x 5/9 x 1.00%',
	# 			'early retirement benefit percentage reduction = 0.00% + 36.0 x 5/9 x 1.00%',
	# 			'early retirement benefit percentage reduction = 20.00%']),
	# 		Instruction(description='Update number of months before normal retirement age', 
	# 			expressions=[f'number of months before normal retirement age = 48 - 36.0',
	# 			f'number of months before normal retirement age = 12.0']),
	# 		Instruction(description='For each month before normal retirement age, add 5/12 of 1.00% to ' \
	# 			'early retirement benefit percentage reduction', 
	# 			expressions=['early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
	# 			'min(number of months before normal retirement age, infinity) x 5/12 of 1.00%',
	# 			'early retirement benefit percentage reduction = 20.00% + min(12.0, infinity) x 5/12 x 1.00%',
	# 			'early retirement benefit percentage reduction = 20.00% + 12.0 x 5/12 x 1.00%',
	# 			'early retirement benefit percentage reduction = 25.00%'])
	# 	]
	# 	self.assertEqual(instructions, err.stepByStep(normal_retirement_age=66, early_retirement_age=62))

	# def test_stepByStep_with_spousal_early_retirement(self):
	# 	err = EarlyRetirementBenefitReduction.objects.get(
	# 		Q(benefit_type=EarlyRetirementBenefitReduction.SPOUSAL) & 
	# 		Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
	# 	)
	# 	instructions = [
	# 		Instruction(description='Get normal retirement age',
	# 			expressions=['normal retirement age = 66']),
	# 		Instruction(description='Get early retirement age',
	# 			expressions=['early retirement age = 62']),
	# 		Instruction(description='Determine if person is eligible for early retirement benefit reduction', 
	# 			expressions=['normal retirement age > early retirement age?',
	# 				'66 > 62?',
	# 				'True']),
	# 		Instruction(description='Determine number of months before normal retirement age', 
	# 			expressions=['number of months before normal retirement age = | early retirement age - normal retirement age | * 12',
	# 			'number of months before normal retirement age = | 62 - 66 | * 12',
	# 			'number of months before normal retirement age = 4 * 12',
	# 			'number of months before normal retirement age = 48']),
	# 		Instruction('Set early retirement benefit percentage reduction to zero', 
	# 			['early retirement benefit percentage reduction = 0.00%']),
	# 		Instruction(description='For each month (up to 36.0 months) before normal retirement age, add 25/36 of 1.00% to ' \
	# 			'early retirement benefit percentage reduction', 
	# 			expressions=['early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
	# 			'min(number of months before normal retirement age, 36.0) x 25/36 of 1.00%',
	# 			'early retirement benefit percentage reduction = 0.00% + min(48, 36.0) x 25/36 x 1.00%',
	# 			'early retirement benefit percentage reduction = 0.00% + 36.0 x 25/36 x 1.00%',
	# 			'early retirement benefit percentage reduction = 25.00%']),
	# 		Instruction(description='Update number of months before normal retirement age', 
	# 			expressions=[f'number of months before normal retirement age = 48 - 36.0',
	# 			f'number of months before normal retirement age = 12.0']),
	# 		Instruction(description='For each month before normal retirement age, add 5/12 of 1.00% to ' \
	# 			'early retirement benefit percentage reduction', 
	# 			expressions=['early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
	# 			'min(number of months before normal retirement age, infinity) x 5/12 of 1.00%',
	# 			'early retirement benefit percentage reduction = 25.00% + min(12.0, infinity) x 5/12 x 1.00%',
	# 			'early retirement benefit percentage reduction = 25.00% + 12.0 x 5/12 x 1.00%',
	# 			'early retirement benefit percentage reduction = 30.00%'])
	# 	]
	# 	self.assertEqual(instructions, err.stepByStep(normal_retirement_age=66, early_retirement_age=62))

	# def test_stepByStep_with_survivor_early_retirement(self):
	# 	err = EarlyRetirementBenefitReduction.objects.get(
	# 		Q(benefit_type=EarlyRetirementBenefitReduction.SURVIVOR) & 
	# 		Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
	# 	)
	# 	instructions = [
	# 		Instruction(description='Get normal retirement age',
	# 			expressions=['normal retirement age = 66']),
	# 		Instruction(description='Get early retirement age',
	# 			expressions=['early retirement age = 62']),
	# 		Instruction(description='Determine if person is eligible for early retirement benefit reduction', 
	# 			expressions=['normal retirement age > early retirement age?',
	# 				'66 > 62?',
	# 				'True']),
	# 		Instruction(description='Determine number of months before normal retirement age', 
	# 			expressions=['number of months before normal retirement age = | early retirement age - normal retirement age | * 12',
	# 			'number of months before normal retirement age = | 62 - 66 | * 12',
	# 			'number of months before normal retirement age = 4 * 12',
	# 			'number of months before normal retirement age = 48']),
	# 		Instruction('Set early retirement benefit percentage reduction to zero', 
	# 			['early retirement benefit percentage reduction = 0.00%']),
	# 		Instruction(description='For each month before normal retirement age, add 0.59% to ' \
	# 			'early retirement benefit percentage reduction', 
	# 			expressions=['early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
	# 			'number of months before normal retirement age x 0.59%',
	# 			'early retirement benefit percentage reduction = 0.00% + 48 x 0.59%',
	# 			'early retirement benefit percentage reduction = 28.50%'])
	# 	]
	# 	self.assertEqual(instructions, err.stepByStep(normal_retirement_age=66, early_retirement_age=62))