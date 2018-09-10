from rest_framework import viewsets, serializers
from NEOandNDEBenefitCalculator.models import Respondent
from NEOandNDEBenefitCalculator.serializers import RespondentSerializer
from BenefitRule.views import PersonViewSet

# fix to able to post only
class RespondentViewSet(PersonViewSet):
	queryset = Respondent.objects.all()
	serializer_class = RespondentSerializer