from rest_framework import serializers
from BenefitRule.models import Person, Relationship
from NEOandNDEBenefitCalculator.models import Respondent

from BenefitRule.serializers import PersonSerializer
from NEOandNDEBenefitCalculator.serializers import RespondentSerializer

from generic_relations.relations import GenericRelatedField

class RelationshipSerializer(serializers.ModelSerializer):
	object_id1 = serializers.IntegerField(required=False)
	object_id2 = serializers.IntegerField(required=False)
	content_object1 = GenericRelatedField({
		Person: serializers.HyperlinkedRelatedField(
			queryset = Person.objects.all(),
			view_name='person-detail',
		),
		Respondent: serializers.HyperlinkedRelatedField(
			queryset = Respondent.objects.all(),
			view_name='respondent-detail',
		),
	})

	content_object2 = GenericRelatedField({
		Person: serializers.HyperlinkedRelatedField(
			queryset = Person.objects.all(),
			view_name='person-detail',
		),
		Respondent: serializers.HyperlinkedRelatedField(
			queryset = Respondent.objects.all(),
			view_name='respondent-detail',
		),
	})

	class Meta:
		model = Relationship
		fields = ('id', 'object_id1', 'object_id2', 'content_object1', 'content_object2', 'person1_role', 'person2_role', 'relationship_type', 'start_date', 'end_date')