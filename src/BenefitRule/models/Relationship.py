from django.db import models
from .Person import Person

class Relationship(models.Model):
	person1 = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='person1')
	person2 = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='person2')	
	HUSBAND = 'H'
	WIFE = 'W'
	ROLE_TYPE_CHOICES = (
		(HUSBAND, 'Husband'),
		(WIFE, 'Wife')
	)
	person1_role = models.CharField(
		max_length=1,
		choices=ROLE_TYPE_CHOICES,
		null=True
	)
	person2_role = models.CharField(
		max_length=1,
		choices=ROLE_TYPE_CHOICES,
		null=True
	)
	MARRIED = 'M'
	RELATIONSHIP_TYPE_CHOICES = (
		(MARRIED, 'Married'),
	)
	relationship_type = models.CharField(
		max_length=1,
		choices=RELATIONSHIP_TYPE_CHOICES,
		null=True
	)
	start_date = models.DateField(null=True, blank=True)
	end_date = models.DateField(null=True, blank=True)

	def getOtherPerson(self, person):
		if person == self.person1:
			return self.person2
		else:
			return self.person1