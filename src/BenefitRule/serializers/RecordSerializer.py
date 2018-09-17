from rest_framework import serializers
from BenefitRule.models import Record, Person
from NEOandNDEBenefitCalculator.models import Respondent
from NEOandNDEBenefitCalculator.serializers import RespondentSerializer
from .MoneySerializer import MoneySerializer
from .PersonSerializer import PersonSerializer
from generic_relations.relations import GenericRelatedField

class RecordSerializer(serializers.ModelSerializer):
	content_object = GenericRelatedField({
		Person: PersonSerializer(),
		Respondent: RespondentSerializer()
	})

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
		fields = ('id', 'object_id', 'content_object',
			'earliest_retirement_age', 'normal_retirement_age', 
			'average_indexed_monthly_covered_earning', 'basic_primary_insurance_amount', 
			'wep_primary_insurance_amount', 'average_indexed_monthly_non_covered_earning', 
			'monthly_non_covered_pension', 'wep_reduction', 'final_primary_insurance_amount',
			'max_delay_retirement_credit', 'delay_retirement_credit', 
			'max_early_retirement_reduction', 'early_retirement_reduction',
			'benefit', 'government_pension_offset', 'spousal_insurance_benefit', 
			'survivor_insurance_benefit')