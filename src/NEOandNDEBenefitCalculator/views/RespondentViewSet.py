from rest_framework import viewsets, serializers
from NEOandNDEBenefitCalculator.models import Respondent
from NEOandNDEBenefitCalculator.serializers import RespondentSerializer
from .CustomMixin import CreateListMixin

# fix to able to post only
class RespondentViewSet(viewsets.ModelViewSet):
	queryset = Respondent.objects.all()
	serializer_class = RespondentSerializer