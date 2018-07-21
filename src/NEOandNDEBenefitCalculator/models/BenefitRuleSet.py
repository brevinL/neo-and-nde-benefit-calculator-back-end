from django.db import models
# from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _
from .RetirementAge import RetirementAge
from .AIME import AverageIndexedMonthlyEarning
from .DRC import DelayRetirementCredit
from .ERR import EarlyRetirementBenefitReduction
from .PIA import PrimaryInsuranceAmount
from .SpousalInsuranceBenefit import SpousalInsuranceBenefit
from .WEP import WindfallEliminationProvision
from .GPO import GovernmentPensionOffset
from .SurvivorInsuranceBenefit import SurvivorInsuranceBenefit
# def validate_normal_retirement_age_law(value):
# 	print(value)
# 	if value % 2 != 0:
# 		raise ValidationError(
# 			_('%(value)s is not an even number'),
# 			params={'value': value},
# 		)

# experiment with validators if possible with foreign key
# https://docs.djangoproject.com/en/2.0/ref/validators/
class BenefitRuleSet(models.Model):
	earliest_retirement_age_law = models.ForeignKey(RetirementAge, on_delete=models.CASCADE, null=True, related_name='earliest_retirement_age_law')
	normal_retirement_age_law = models.ForeignKey(RetirementAge, on_delete=models.CASCADE, null=True, related_name='normal_retirement_age_law')
	aime_law = models.ForeignKey(AverageIndexedMonthlyEarning, on_delete=models.CASCADE, null=True, related_name='aime_law')
	pia_law = models.ForeignKey(PrimaryInsuranceAmount, on_delete=models.CASCADE, null=True, related_name='pia_law') 
	wep_pia_law = models.ForeignKey(PrimaryInsuranceAmount, on_delete=models.CASCADE, null=True, related_name='wep_pia_law') 
	wep_law = models.ForeignKey(WindfallEliminationProvision, on_delete=models.CASCADE, null=True, related_name='wep_law')
	drc_law = models.ForeignKey(DelayRetirementCredit, on_delete=models.CASCADE, null=True, related_name='drc_law')
	primary_err_law = models.ForeignKey(EarlyRetirementBenefitReduction, on_delete=models.CASCADE, null=True, related_name='primary_err_law')
	gpo_law = models.ForeignKey(GovernmentPensionOffset, on_delete=models.CASCADE, null=True, related_name='gpo_law') 
	spousal_insurance_benefit_law = models.ForeignKey(SpousalInsuranceBenefit, on_delete=models.CASCADE, null=True, related_name='spousal_insurance_benefit_law')
	survivor_insurance_benefit_law = models.ForeignKey(SurvivorInsuranceBenefit, on_delete=models.CASCADE, null=True, related_name='survivor_insurance_benefit_law')