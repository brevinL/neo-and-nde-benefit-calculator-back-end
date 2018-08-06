from rest_framework import serializers
from BenefitRule.models import Money
from NEOandNDEBenefitCalculator.models import Respondent
from .MoneySerializer import MoneySerializer

class RespondentListSerializer(serializers.ListSerializer):
	def create(self, validated_data):
		respondents = []
		for item in validated_data:
			annual_covered_earning = item.get('annual_covered_earning')
			item['annual_covered_earning'] = Money.objects.create(amount=annual_covered_earning.get('amount', 0))
			annual_non_covered_earning = item.get('annual_non_covered_earning')
			item['annual_non_covered_earning'] = Money.objects.create(amount=annual_non_covered_earning.get('amount', 0))
			respondents.append(Respondent.objects.create(**item))
		return respondents
		
class RespondentSerializer(serializers.ModelSerializer):
	# id = serializers.IntegerField() 
	# alias = serializers.CharField(allow_null=True)
	annual_covered_earning = MoneySerializer()
	annual_non_covered_earning = MoneySerializer()
	# spousal_early_retirement_reduction = MoneySerializer()
	# survivor_early_retirement_reduction = MoneySerializer()

	class Meta:
		model = Respondent
		fields = ('id', 'year_of_birth', 'years_of_covered_earnings', 'annual_covered_earning',
			'years_of_non_covered_earnings', 'annual_non_covered_earning',
			'fraction_of_non_covered_aime_to_non_covered_pension',
			'early_retirement_reduction', 'delay_retirement_credit',
			'spousal_early_retirement_reduction', 'survivor_early_retirement_reduction')
		list_serializer_class = RespondentListSerializer