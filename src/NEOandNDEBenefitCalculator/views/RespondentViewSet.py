from rest_framework import status, viewsets, serializers
from NEOandNDEBenefitCalculator.models import *
from NEOandNDEBenefitCalculator.serializers import *
from .CustomMixin import CreateListMixin

class RespondentViewSet(CreateListMixin, viewsets.ModelViewSet):
	queryset = Respondent.objects.all()
	serializer_class = RespondentSerializer