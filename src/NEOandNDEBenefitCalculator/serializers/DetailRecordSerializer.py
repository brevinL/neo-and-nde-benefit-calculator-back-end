from rest_framework import serializers
from .InstructionSerializer import InstructionSerializer

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