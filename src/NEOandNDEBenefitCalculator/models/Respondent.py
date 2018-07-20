from django.db import models
from BenefitRule.models import Money, Person

class Respondent(Person):
	years_of_covered_earnings = models.IntegerField()
	annual_covered_earning = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="annual_covered_earning") 
	years_of_non_covered_earnings = models.IntegerField()
	annual_non_covered_earning = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="annual_non_covered_earning") 
	fraction_of_non_covered_aime_to_non_covered_pension = models.FloatField()
	early_retirement_reduction = models.FloatField()
	delay_retirement_credit = models.FloatField()
	spousal_early_retirement_reduction = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="spousal_early_retirement_reduction") 
	survivor_early_retirement_reduction = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="survivor_early_retirement_reduction") 

	@property
	def annual_covered_earnings(self):
		return [Money(amount=self.annual_covered_earning.amount) for earning in range(self.years_of_covered_earnings)]

	@property
	def annual_non_covered_earnings(self):
		return [Money(amount=self.annual_non_covered_earning.amount) for earning in range(self.years_of_non_covered_earnings)]
