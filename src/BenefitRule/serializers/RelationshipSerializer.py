from rest_framework import serializers
from BenefitRule.models import Relationship

class RelationshipListSerializer(serializers.ListSerializer):
	def create(self, validated_data):
		relationships = [Relationship(**item) for item in validated_data]
		return relationships

class RelationshipSerializer(serializers.ModelSerializer):
	person1_id = serializers.IntegerField()
	person2_id = serializers.IntegerField()

	class Meta:
		model = Relationship
		fields = ('person1_id', 'person2_id', 'relationship_type')
		list_serializer_class = RelationshipListSerializer