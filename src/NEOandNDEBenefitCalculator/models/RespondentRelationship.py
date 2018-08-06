from django.db import models
from BenefitRule.models import Relationship
from .Respondent import Respondent

class RespondentRelationship(Relationship):
	person1 = models.ForeignKey(Respondent, on_delete=models.CASCADE, related_name='person1')
	person2 = models.ForeignKey(Respondent, on_delete=models.CASCADE, related_name='person2')	