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
		fields = '__all__'