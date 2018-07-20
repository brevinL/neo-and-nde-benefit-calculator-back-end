from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Factor, FactorPiece, Money, ordinal, currency

class FactorTestCase(TestCase):
	def setUp(self):
		f1 = Factor.objects.create(id=1, order=1)
		FactorPiece.objects.create(inital_factor=0.40, min_year_of_coverage=-inf, max_year_of_coverage=20, order=1, factor=f1)
		FactorPiece.objects.create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2, factor=f1)
		FactorPiece.objects.create(inital_factor=0.90, min_year_of_coverage=30, max_year_of_coverage=inf, order=3, factor=f1)

		f2 = Factor.objects.create(id=2, order=1)
		FactorPiece.objects.create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2, factor=f2)

	def test_calculate_no_pieces(self):
		f = Factor.objects.create(order=1)
		with self.assertRaises(ObjectDoesNotExist):
			f.calculate(year_of_coverage=0)

	def test_calculate_within_range(self):
		factor = Factor.objects.get(id=1)
		self.assertAlmostEqual(0.40, factor.calculate(year_of_coverage=0))

	def test_calculate_out_of_bound(self):
		factor = Factor.objects.get(id=2)
		with self.assertRaises(ObjectDoesNotExist):
			factor.calculate(year_of_coverage=0)

class FactorPieceTestCase(TestCase):
	def test_calculate_without_years_of_coverage(self):
		factor_piece = FactorPiece.objects.create(inital_factor=0.90, order=1)
		self.assertAlmostEqual(0.90, factor_piece.calculate(year_of_coverage=0))

	def test_calculate_with_years_of_coverage_within_finite_year_of_coverage_range(self):
		factor_piece = FactorPiece.objects.create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2)
		self.assertAlmostEqual(0.45, factor_piece.calculate(year_of_coverage=21))
		self.assertAlmostEqual(0.65, factor_piece.calculate(year_of_coverage=25))
		self.assertAlmostEqual(0.85, factor_piece.calculate(year_of_coverage=29))

	def test_calculate_with_years_of_coverage_out_of_bound_of_finite_year_of_coverage_range(self):
		factor_piece = FactorPiece.objects.create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2)
		with self.assertRaises(ValueError):
			factor_piece.calculate(year_of_coverage=0)

	def test_calculate_with_years_of_coverage_within_infinite_year_of_coverage_range(self):
		factor_piece = FactorPiece.objects.create(inital_factor=0.90, min_year_of_coverage=30, max_year_of_coverage=inf, order=3)
		self.assertAlmostEqual(0.90, factor_piece.calculate(year_of_coverage=30))
		self.assertAlmostEqual(0.90, factor_piece.calculate(year_of_coverage=31))

		factor_piece = FactorPiece.objects.create(inital_factor=0.40, min_year_of_coverage=-inf, max_year_of_coverage=20, order=1)
		self.assertAlmostEqual(0.40, factor_piece.calculate(year_of_coverage=20))
		self.assertAlmostEqual(0.40, factor_piece.calculate(year_of_coverage=19))