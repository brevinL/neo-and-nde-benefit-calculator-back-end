from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .BenefitRule import BenefitRule

class Instruction(models.Model):
	order = models.IntegerField()
	description = models.TextField()

	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

class Expression(models.Model):
	instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name="instruction")
	description = models.TextField()