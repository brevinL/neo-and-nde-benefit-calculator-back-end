from rest_framework import serializers
from NEOandNDEBenefitCalculator.models import Respondent
from BenefitRule.models import Money, Relationship, Record, BenefitRule

class MoneySerializer(serializers.ModelSerializer):
	class Meta:
		model = Money
		fields = ('amount', )

class RespondentListSerializer(serializers.ListSerializer):
	def create(self, validated_data):
		respondents = []
		for item in validated_data:
			annual_covered_earning = item.get('annual_covered_earning')
			item['annual_covered_earning'] = Money(amount=annual_covered_earning.get('amount', 0))
			annual_non_covered_earning = item.get('annual_non_covered_earning')
			item['annual_non_covered_earning'] = Money(amount=annual_non_covered_earning.get('amount', 0))
			spousal_early_retirement_reduction = item.get('spousal_early_retirement_reduction')
			item['spousal_early_retirement_reduction'] = Money(amount=spousal_early_retirement_reduction.get('amount', 0))
			survivor_early_retirement_reduction = item.get('survivor_early_retirement_reduction')
			item['survivor_early_retirement_reduction'] = Money(amount=survivor_early_retirement_reduction.get('amount', 0))
			respondents.append(Respondent(**item))
		return respondents
		
class RespondentSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField() 
	annual_covered_earning = MoneySerializer()
	annual_non_covered_earning = MoneySerializer()
	spousal_early_retirement_reduction = MoneySerializer()
	survivor_early_retirement_reduction = MoneySerializer()

	class Meta:
		model = Respondent
		fields = ('id', 'year_of_birth', 'years_of_covered_earnings', 'annual_covered_earning',
			'years_of_non_covered_earnings', 'annual_non_covered_earning',
			'fraction_of_non_covered_aime_to_non_covered_pension',
			'early_retirement_reduction', 'delay_retirement_credit',
			'spousal_early_retirement_reduction', 'survivor_early_retirement_reduction')
		list_serializer_class = RespondentListSerializer

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

class RecordSerializer(serializers.ModelSerializer):
	person_id = serializers.IntegerField()
	average_indexed_monthly_covered_earning = MoneySerializer()
	basic_primary_insurance_amount = MoneySerializer()
	wep_primary_insurance_amount = MoneySerializer()
	average_indexed_monthly_non_covered_earning = MoneySerializer()
	monthly_non_covered_pension = MoneySerializer()
	wep_reduction = MoneySerializer()
	final_primary_insurance_amount = MoneySerializer()
	benefit = MoneySerializer()
	government_pension_offset = MoneySerializer()
	spousal_insurance_benefit = MoneySerializer()
	survivor_insurance_benefit = MoneySerializer()

	class Meta:
		model = Record
		fields = ('person_id', 'earliest_retirement_age', 'normal_retirement_age',
			'average_indexed_monthly_covered_earning', 'basic_primary_insurance_amount',
			'wep_primary_insurance_amount', 'average_indexed_monthly_non_covered_earning',
			'monthly_non_covered_pension', 'wep_reduction', 'final_primary_insurance_amount',
			'delay_retirement_credit', 'early_retirement_reduction', 'benefit', 'government_pension_offset',
			'spousal_insurance_benefit', 'survivor_insurance_benefit')

class BenefitRuleSerializer(serializers.ModelSerializer):
	class Meta:
		model = BenefitRule
		fields = ('start_date', 'end_date')

class StringListField(serializers.ListField):
    child = serializers.CharField()

class InstructionSerializer(serializers.Serializer):
	description = serializers.CharField()
	expressions = StringListField()

class DetailRecordSerializer(serializers.Serializer):
	person_id = serializers.IntegerField()
	# earliest_retirement_age_instructions = InstructionSerializer()
	# normal_retirement_age_instructions = InstructionSerializer()
	average_indexed_monthly_covered_earning_instructions = InstructionSerializer(many=True, allow_null=True)
	basic_primary_insurance_amount_instructions = InstructionSerializer(many=True, allow_null=True)
	wep_primary_insurance_amount_instructions = InstructionSerializer(many=True, allow_null=True)
	average_indexed_monthly_non_covered_earning_instructions = InstructionSerializer(many=True, allow_null=True)
	monthly_non_covered_pension_instructions = InstructionSerializer(many=True, allow_null=True)
	wep_reduction_instructions = InstructionSerializer(many=True, allow_null=True)
	final_primary_insurance_amount_instructions = InstructionSerializer(many=True, allow_null=True)
	delay_retirement_credit_instructions = InstructionSerializer(many=True, allow_null=True)
	early_retirement_reduction_instructions = InstructionSerializer(many=True, allow_null=True)
	benefit_instructions = InstructionSerializer(many=True, allow_null=True)
	government_pension_offset_instructions = InstructionSerializer(many=True, allow_null=True)
	spousal_insurance_benefit_instructions = InstructionSerializer(many=True, allow_null=True)
	survivor_insurance_benefit_instructions = InstructionSerializer(many=True, allow_null=True)

	# class Meta:
	# 	model = Record
	# 	fields = ('person_id', 
	# 		'average_indexed_monthly_covered_earning_instructions', 'basic_primary_insurance_amount_instructions',
	# 		'wep_primary_insurance_amount_instructions', 'average_indexed_monthly_non_covered_earning_instructions',
	# 		'monthly_non_covered_pension_instructions', 'wep_reduction_instructions', 'final_primary_insurance_amount_instructions',
	# 		'delay_retirement_credit_instructions', 'early_retirement_reduction_instructions', 'benefit_instructions', 'government_pension_offset_instructions',
	# 		'spousal_insurance_benefit_instructions')