from rest_framework import serializers
from BenefitRule.models import Relationship, Person
from NEOandNDEBenefitCalculator.models import Respondent
from generic_relations.relations import GenericRelatedField

# class RelationshipListSerializer(serializers.ListSerializer):
# 	def create(self, validated_data):
# 		relationships = [Relationship(**item) for item in validated_data]
# 		return relationships

class RelationshipSerializer(serializers.ModelSerializer):
	# person1_id = serializers.IntegerField()
	# person2_id = serializers.IntegerField()

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
		fields = ('id', 'object_id1', 'object_id2', 'content_object1', 'content_object2', 
			'person1_role', 'person2_role', 'relationship_type', 'start_date', 'end_date')