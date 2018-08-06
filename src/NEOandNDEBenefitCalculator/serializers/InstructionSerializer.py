from rest_framework import serializers

class StringListField(serializers.ListField):
	child = serializers.CharField()

class InstructionSerializer(serializers.Serializer):
	description = serializers.CharField()
	expressions = StringListField()