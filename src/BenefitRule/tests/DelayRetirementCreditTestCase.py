from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import DelayRetirementCredit, DelayRetirementCreditPiece, Money, ordinal, currency

class DelayRetirementCreditTestCase(TestCase):
	def setUp(self):
		drc = DelayRetirementCredit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), age_limit=70)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.055, min_year=1933, max_year=1934, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.06, min_year=1935, max_year=1936, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.065, min_year=1937, max_year=1938, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.07, min_year=1939, max_year=1940, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.075, min_year=1941, max_year=1942, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.08, min_year=1943, max_year=inf, percentage_rate=0, year_change=1, delay_retirement_credit=drc)

	def test_calculate_no_pieces(self):
		drc = DelayRetirementCredit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), age_limit=70)
		with self.assertRaises(ObjectDoesNotExist):
			drc.calculate(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=80)

	def test_calculate_max_delay_retirement(self):
		drc = DelayRetirementCredit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0.32, drc.calculate(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=80), places=2)

	def test_calculate_no_delay_retirement(self):
		drc = DelayRetirementCredit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0, drc.calculate(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=67), places=2)

	def test_calculate_some_delay_retirement(self):
		drc = DelayRetirementCredit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0.16, drc.calculate(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=68), places=2)

	def test_calculate_out_of_bound_delay_retirement(self):
		drc = DelayRetirementCredit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) & Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(0.00, drc.calculate(year_of_birth=1954, normal_retirement_age=67, delayed_retirement_age=60), places=2)
		
class DelayRetirementCreditPieceTestCase(TestCase):
	def setUp(self):
		DelayRetirementCreditPiece.objects.create(id=1, inital_percentage=0.055, min_year=1933, max_year=1934, percentage_rate=0, year_change=1)
		DelayRetirementCreditPiece.objects.create(id=2, inital_percentage=0.06, min_year=1935, max_year=1936, percentage_rate=0, year_change=1)
		DelayRetirementCreditPiece.objects.create(id=3, inital_percentage=0.065, min_year=1937, max_year=1938, percentage_rate=0, year_change=1)
		DelayRetirementCreditPiece.objects.create(id=4, inital_percentage=0.07, min_year=1939, max_year=1940, percentage_rate=0, year_change=1)
		DelayRetirementCreditPiece.objects.create(id=5, inital_percentage=0.075, min_year=1941, max_year=1942, percentage_rate=0, year_change=1)
		DelayRetirementCreditPiece.objects.create(id=6, inital_percentage=0.08, min_year=1943, max_year=inf, percentage_rate=0, year_change=1)

	def test_calculate_within_finite_range(self):
		drc_piece = DelayRetirementCreditPiece.objects.get(id=1)
		self.assertAlmostEqual(0.055, drc_piece.calculate(year_of_birth=1934))

		drc_piece = DelayRetirementCreditPiece.objects.get(id=2)
		self.assertAlmostEqual(0.06, drc_piece.calculate(year_of_birth=1935))

		drc_piece = DelayRetirementCreditPiece.objects.get(id=5)
		self.assertAlmostEqual(0.075, drc_piece.calculate(year_of_birth=1941))
		self.assertAlmostEqual(0.075, drc_piece.calculate(year_of_birth=1942))

	def test_calculate_within_infinite_range(self):
		drc_piece = DelayRetirementCreditPiece.objects.get(id=6)
		self.assertAlmostEqual(0.08, drc_piece.calculate(year_of_birth=2018))

	def test_calculate_out_of_bound(self):
		drc_piece = DelayRetirementCreditPiece.objects.get(id=1)
		with self.assertRaises(ValueError):
			drc_piece.calculate(year_of_birth=0)