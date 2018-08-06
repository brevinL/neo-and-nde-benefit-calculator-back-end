from rest_framework import serializers
from BenefitRule.models import Record
from .MoneySerializer import MoneySerializer

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