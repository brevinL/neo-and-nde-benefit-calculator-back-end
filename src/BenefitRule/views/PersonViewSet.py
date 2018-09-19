from rest_framework import viewsets
from BenefitRule.models import Person
from BenefitRule.serializers import PersonSerializer

class PersonViewSet(viewsets.ModelViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer