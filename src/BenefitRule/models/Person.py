from django.db import models
from .Money import Money
from .Relationship import Relationship
from django.contrib.contenttypes.fields import GenericRelation

class Person(models.Model): # a person's record
	year_of_birth = models.PositiveIntegerField(null=True)
	retirement_age = models.PositiveIntegerField(null=True)
	relationships1 = GenericRelation(Relationship, related_query_name='person1', content_type_field='content_type1', object_id_field='object_id1')
	relationships2 = GenericRelation(Relationship, related_query_name='person2', content_type_field='content_type2', object_id_field='object_id2')

	@property
	def year_of_retirement(self):
		return self.year_of_birth + self.retirement_age