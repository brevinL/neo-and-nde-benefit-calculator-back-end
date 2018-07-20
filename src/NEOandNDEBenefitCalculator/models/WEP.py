from BenefitRule.models import WindfallEliminationProvision
from .Instruction import Instruction

class WindfallEliminationProvision(WindfallEliminationProvision):
	class Meta:
		proxy = True

	def stepByStep(self, primary_insurance_amount, wep_primary_insurance_amount, monthly_non_covered_pension):
		stepByStep = []
		
		stepByStep.append(Instruction("Get WEP's primary insurance amount",
			["WEP's primary insurance amount = primary insurance amount",
			f"WEP's primary insurance amount = {wep_primary_insurance_amount}"]))

		stepByStep.append(Instruction("Get monthly non covered pension",
			[f"monthly non covered pension = {monthly_non_covered_pension}"]))

		stepByStep.append(Instruction("Get primary insurance amount",
			[f"primary insurance amount = {primary_insurance_amount}"]))

		wep_reduction = min(monthly_non_covered_pension * 1/2, max(primary_insurance_amount - wep_primary_insurance_amount, 0))
		stepByStep.append(Instruction('Find Windfall Elimination Provision reduction', 
			['WEP reduction = min(monthly non covered pension x 1/2, max(primary insurance amount - WEP\'s primary insurance amount, 0))',
			f'WEP reduction = min({monthly_non_covered_pension} x 1/2, max({primary_insurance_amount} - {wep_primary_insurance_amount}, 0))',
			f'WEP reduction = min({monthly_non_covered_pension * 1/2}, max({primary_insurance_amount - wep_primary_insurance_amount}, 0)',
			f'WEP reduction = min({monthly_non_covered_pension * 1/2}, {max(primary_insurance_amount - wep_primary_insurance_amount, 0)})',
			f'WEP reduction = {wep_reduction}']))

		return stepByStep