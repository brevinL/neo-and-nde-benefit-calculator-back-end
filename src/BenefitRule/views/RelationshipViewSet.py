from rest_framework import status, viewsets, serializers
from BenefitRule.models import Relationship
from BenefitRule.serializers import RelationshipSerializer

# fix to able to post only
class RelationshipViewSet(viewsets.ModelViewSet):
	queryset = Relationship.objects.all()
	serializer_class = RelationshipSerializer