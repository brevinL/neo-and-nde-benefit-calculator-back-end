from math import floor
from django.db import models
from .Person import Person 
from .Money import Money

# https://secure.ssa.gov/poms.nsf/lnx/0101310010#c
class Earning(models.Model):
	money = models.ForeignKey(Money, on_delete=models.CASCADE)

	COVERED = 'C'
	NONCOVERED = 'N'
	TYPE_OF_EARNING_CHOICES = (
		(COVERED, 'Covered'),
		(NONCOVERED, 'Non-covered')
	)
	type_of_earning = models.CharField(
		max_length=1,
		choices=TYPE_OF_EARNING_CHOICES,
	)

	YEARLY = 'Y'
	MONTHLY = 'M'
	TIME_PERIOD_CHOICES = (
		(YEARLY, 'Yearly'),
		(MONTHLY, 'Monthly'),
	)
	time_period = models.CharField(
		max_length=1,
		choices=TIME_PERIOD_CHOICES,
	)

	person = models.ForeignKey(Person, on_delete=models.CASCADE)