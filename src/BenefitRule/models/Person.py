from django.db import models
from .Money import Money

class Person(models.Model): # a person's record
	year_of_birth = models.PositiveIntegerField(null=True)