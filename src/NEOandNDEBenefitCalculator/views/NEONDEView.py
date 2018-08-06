from datetime import date
from math import inf
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Q
from django.shortcuts import render, get_object_or_404
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from BenefitRule.models import Person, Money, Relationship, Record
from NEOandNDEBenefitCalculator.models import *
from NEOandNDEBenefitCalculator.serializers import *

class CalculatorViewSet(viewsets.ViewSet):
	renderer_classes = (JSONRenderer, )

	@list_route(methods=['post'])
	def summary(self, request): # given an inital record -> applied benefit rules to record -> update record
		# http://www.django-rest-framework.org/api-guide/serializers/#dealing-with-multiple-objects
		respondents = self.serializeRespondents(data=request.data.pop('respondents', []))
		relationships = self.serializeRelationships(data=request.data.pop('relationships', []))

		# have to change manually each year because you got to 
		# add in the numbers for the other laws to db anyways
		benefit_rules = self.setUpBenefitRules(year=2016)

		records = []
		for respondent in respondents: 
			record = self.calculateRetirementBenefits(benefit_rules=benefit_rules, respondent=respondent)
			records.append(record)

		for record in records:
			respondent_relationships = list(filter(lambda relationship: relationship.person1_id == record.person_id or relationship.person2_id == record.person_id, relationships))
			for relationship in respondent_relationships:
				spouse_id = relationship.person2_id if relationship.person1_id == record.person_id else relationship.person1_id
				spouse_record = list(filter(lambda record: record.person_id == spouse_id, records))[0]
				self.calculateDependentBenefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
				self.calculateSurvivorBenefits(benefit_rules=benefit_rules, respondent=respondent, beneficiary_record=record, spousal_beneficiary_record=spouse_record)

		record_serializer = RecordSerializer(records, many=True)
		return Response({'records': record_serializer.data}, content_type='application/json;charset=utf-8')

	@list_route(methods=['post'])
	def stepByStep(self, request):# given an inital record -> applied benefit rules to record -> update record
		# http://www.django-rest-framework.org/api-guide/serializers/#dealing-with-multiple-objects
		respondents = self.serializeRespondents(data=request.data.pop('respondents', []))
		relationships = self.serializeRelationships(data=request.data.pop('relationships', []))

		# have to change manually each year because you got to 
		# add in the numbers for the other laws to db anyways
		benefit_rules = self.setUpBenefitRules(year=2016)

		records = []
		detail_records = []
		for respondent in respondents: 
			record = self.calculateRetirementBenefits(benefit_rules=benefit_rules, respondent=respondent)
			records.append(record)

			detail_record = self.getRetirementBenefitsInstructions(benefit_rules=benefit_rules, respondent=respondent, beneficiary_record=record)
			detail_records.append(detail_record)

		for record in records:
			respondent_relationships = list(filter(lambda relationship: relationship.person1_id == record.person_id or relationship.person2_id == record.person_id, relationships))
			for relationship in respondent_relationships:
				spouse_id = relationship.person2_id if relationship.person1_id == record.person_id else relationship.person1_id
				spouse_record = list(filter(lambda record: record.person_id == spouse_id, records))[0]

				self.calculateDependentBenefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
				self.calculateSurvivorBenefits(benefit_rules=benefit_rules, respondent=respondent, beneficiary_record=record, spousal_beneficiary_record=spouse_record)

				detail_record = list(filter(lambda detail_record: detail_record.person_id == record.person_id, detail_records))[0]
				self.getDependentBenefitsInstructions(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)
				# doesnt accept empty list of instructions
				# self.getSurvivorBenefitsInstructions(benefit_rules=benefit_rules, respondent=respondent, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)
				
		detail_record_serializer = DetailRecordSerializer(detail_records, many=True)
		return Response({'detail_records': detail_record_serializer.data}, content_type='application/json;charset=utf-8')

	# cannot handle failures atm, must handle the response to be directed to the @post and not here
	def serializeRespondents(self, data):
		respondent_serializer = RespondentSerializer(data=data, many=True, allow_empty=False)
		if(not respondent_serializer.is_valid()):
			return Response(respondent_serializer.errors, status.HTTP_400_BAD_REQUEST)
		return respondent_serializer.create(respondent_serializer.validated_data)

	# cannot handle failures atm
	def serializeRelationships(self, data):
		relationship_serializer = RelationshipSerializer(data=data, many=True, allow_empty=False)
		if not relationship_serializer.is_valid():
			return Response(relationship_serializer.errors, status.HTTP_400_BAD_REQUEST)
		return relationship_serializer.create(relationship_serializer.validated_data)

	def setUpBenefitRules(self, year):
		try:
			earliest_retirement_age_law = RetirementAge.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)) &
				Q(retirement_type=RetirementAge.EARLIEST)
			)
			normal_retirement_age_law = RetirementAge.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)) &
				Q(retirement_type=RetirementAge.NORMAL)
			)
			aime_law = AverageIndexedMonthlyEarning.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31))
			)
			pia_law = PrimaryInsuranceAmount.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)),
				type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
			)
			wep_pia_law = PrimaryInsuranceAmount.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)),
				type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP
			)
			wep_law = WindfallEliminationProvision.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31))
			)
			drc_law = DelayRetirementCredit.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31))
			)
			primary_err_law = EarlyRetirementBenefitReduction.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)) &
				Q(benefit_type=EarlyRetirementBenefitReduction.PRIMARY)
			)
			gpo_law = GovernmentPensionOffset.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31))
			)
			spousal_insurance_benefit_law = SpousalInsuranceBenefit.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31))
			)
			survivor_insurance_benefit_law = SurvivorInsuranceBenefit.objects.get(
				Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31))
			)
		except ObjectDoesNotExist as dne:
			raise NotFound(detail=dne, code=status.HTTP_500_INTERNAL_SERVER_ERROR)

		try:
			return BenefitRuleSet.objects.get(
				earliest_retirement_age_law=earliest_retirement_age_law, 
				normal_retirement_age_law=normal_retirement_age_law, 
				aime_law=aime_law, 
				pia_law=pia_law, 
				wep_pia_law=wep_pia_law,
				wep_law=wep_law, 
				drc_law=drc_law, 
				primary_err_law=primary_err_law, 
				gpo_law=gpo_law, 
				spousal_insurance_benefit_law=spousal_insurance_benefit_law, 
				survivor_insurance_benefit_law=survivor_insurance_benefit_law)
		except BenefitRuleSet.DoesNotExist:
			return BenefitRuleSet.objects.create(
				earliest_retirement_age_law=earliest_retirement_age_law, 
				normal_retirement_age_law=normal_retirement_age_law, 
				aime_law=aime_law, 
				pia_law=pia_law, 
				wep_pia_law=wep_pia_law,
				wep_law=wep_law, 
				drc_law=drc_law, 
				primary_err_law=primary_err_law, 
				gpo_law=gpo_law, 
				spousal_insurance_benefit_law=spousal_insurance_benefit_law, 
				survivor_insurance_benefit_law=survivor_insurance_benefit_law)

	def calculateRetirementBenefits(self, benefit_rules, respondent):
		record = Record(person_id=respondent.id)
		# record.year_of_birth = respondent.year_of_birth
		record.earliest_retirement_age = benefit_rules.earliest_retirement_age_law.calculate(year_of_birth=respondent.year_of_birth)
		record.normal_retirement_age = benefit_rules.normal_retirement_age_law.calculate(year_of_birth=respondent.year_of_birth)
		record.average_indexed_monthly_covered_earning = benefit_rules.aime_law.calculate(taxable_earnings=respondent.annual_covered_earnings)
		record.basic_primary_insurance_amount = benefit_rules.pia_law.calculate(
			average_indexed_monthly_earning=record.average_indexed_monthly_covered_earning, 
			year_of_coverage=0)
		record.wep_primary_insurance_amount = benefit_rules.wep_pia_law.calculate(
			average_indexed_monthly_earning=record.average_indexed_monthly_covered_earning,
			year_of_coverage=respondent.years_of_covered_earnings)
		record.average_indexed_monthly_non_covered_earning = benefit_rules.aime_law.calculate(taxable_earnings=respondent.annual_non_covered_earnings)
		record.monthly_non_covered_pension = record.average_indexed_monthly_non_covered_earning * respondent.fraction_of_non_covered_aime_to_non_covered_pension
		record.government_pension_offset = benefit_rules.gpo_law.calculate(monthly_non_covered_pension=record.monthly_non_covered_pension)
		record.wep_reduction = benefit_rules.wep_law.calculate(
			primary_insurance_amount=record.basic_primary_insurance_amount, 
			wep_primary_insurance_amount=record.wep_primary_insurance_amount,
			monthly_non_covered_pension=record.monthly_non_covered_pension)
		record.final_primary_insurance_amount = record.basic_primary_insurance_amount - record.wep_reduction
		record.max_delay_retirement_credit = benefit_rules.drc_law.calculate(
			year_of_birth=respondent.year_of_birth, 
			normal_retirement_age=record.normal_retirement_age, 
			delayed_retirement_age=benefit_rules.drc_law.age_limit)
		record.delay_retirement_credit = min(record.max_delay_retirement_credit, respondent.delay_retirement_credit)
		record.max_early_retirement_reduction = benefit_rules.primary_err_law.calculate(normal_retirement_age=record.normal_retirement_age, 
			early_retirement_age=record.earliest_retirement_age)
		record.early_retirement_reduction = min(record.max_early_retirement_reduction, respondent.early_retirement_reduction)
		record.benefit = record.final_primary_insurance_amount * (1 + (record.delay_retirement_credit - record.early_retirement_reduction))
		return record

	def calculateDependentBenefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record):
		beneficiary_record.spousal_insurance_benefit = benefit_rules.spousal_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount,
			government_pension_offset=beneficiary_record.government_pension_offset) # seperate gpo if spousal insurance benefit before gpo is used somewhere else like basic pia
		return beneficiary_record

	def calculateSurvivorBenefits(self, benefit_rules, respondent, beneficiary_record, spousal_beneficiary_record):
		beneficiary_record.survivor_insurance_benefit = benefit_rules.survivor_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_record.benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=respondent.survivor_early_retirement_reduction, 
			spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
			government_pension_offset=beneficiary_record.government_pension_offset)
		return beneficiary_record

	def getRetirementBenefitsInstructions(self, benefit_rules, respondent, beneficiary_record):
		detail_record = DetailRecord(person_id=respondent.id)
		# detail_record.earliest_retirement_age_instructions = earliest_retirement_age_law.stepByStep(year_of_birth=respondent.year_of_birth)
		# detail_record.normal_retirement_age_instructions = normal_retirement_age_law.stepByStep(year_of_birth=respondent.year_of_birth)
		detail_record.average_indexed_monthly_covered_earning_instructions = benefit_rules.aime_law.stepByStep(taxable_earnings=respondent.annual_covered_earnings)
		detail_record.basic_primary_insurance_amount_instructions = benefit_rules.pia_law.stepByStep(
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning, 
			year_of_coverage=0)
		detail_record.wep_primary_insurance_amount_instructions = benefit_rules.wep_pia_law.stepByStep(
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning,
			year_of_coverage=respondent.years_of_covered_earnings)
		detail_record.average_indexed_monthly_non_covered_earning_instructions = benefit_rules.aime_law.stepByStep(taxable_earnings=respondent.annual_non_covered_earnings)
		detail_record.government_pension_offset_instructions = benefit_rules.gpo_law.stepByStep(monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)
		detail_record.monthly_non_covered_pension_instructions = [
			Instruction(description='Get average indexed monthly non covered earning',
				expressions=[f'average indexed monthly non covered earning = {beneficiary_record.average_indexed_monthly_non_covered_earning}']),
			Instruction(description='Get fraction of non covered AIME to non covered pension',
				expressions=[f'fraction of non covered AIME to non covered pension = {respondent.fraction_of_non_covered_aime_to_non_covered_pension}']),
			Instruction(description='Multiply average indexed monthly non covered earning with the fraction that was coverted from non covered AIME to non covered pension', 
				expressions=[
					'monthly_non_covered_pension = average indexed monthly non covered earning x fraction of non covered AIME to non covered pension',
					f'monthly_non_covered_pension = {beneficiary_record.average_indexed_monthly_non_covered_earning} x {respondent.fraction_of_non_covered_aime_to_non_covered_pension}',
					f'monthly_non_covered_pension = {beneficiary_record.monthly_non_covered_pension}'])] 
		detail_record.wep_reduction_instructions = benefit_rules.wep_law.stepByStep(
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			wep_primary_insurance_amount=beneficiary_record.wep_primary_insurance_amount,
			monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)
		detail_record.final_primary_insurance_amount_instructions = [
			Instruction(description='Get primary insurance amount', expressions=[f'primary insurance amount = {beneficiary_record.basic_primary_insurance_amount}']),
			Instruction(description='Get windfall elimination provision amount', expressions=[f'windfall elimination provision amount = {beneficiary_record.wep_reduction}']),
			Instruction(description='Recalculate primary insurance amount by reducing the primary insurance amount with the windfall elimination provision amount', 
				expressions=[
					'primary insurance amount  = primary insurance amount - windfall elimination provision',
					f'primary insurance amount  = {beneficiary_record.basic_primary_insurance_amount} - {beneficiary_record.wep_reduction}',
					f'primary insurance amount = {beneficiary_record.final_primary_insurance_amount}'])]
		detail_record.delay_retirement_credit_instructions = benefit_rules.drc_law.stepByStep(
			year_of_birth=respondent.year_of_birth, 
			normal_retirement_age=beneficiary_record.normal_retirement_age, 
			delayed_retirement_age=benefit_rules.drc_law.age_limit)
		detail_record.delay_retirement_credit_instructions.append(
			Instruction(description='Get respondent\'s delay retirement credit',
				expressions=[f'respondent\'s delay retirement credit = {percentage(respondent.delay_retirement_credit)}']))
		detail_record.delay_retirement_credit_instructions.append(
			Instruction(description='Cap Delay Retirement Credit', 
				expressions=[
					'delay retirement credit = min(max delay retirement credit, respondent\'s delay retirement credit',
					f'delay retirement credit = min({percentage(beneficiary_record.max_delay_retirement_credit)}, {percentage(respondent.delay_retirement_credit)})',
					f'delay retirement credit = {percentage(beneficiary_record.delay_retirement_credit)}'])) 
		detail_record.early_retirement_reduction_instructions = benefit_rules.primary_err_law.stepByStep(normal_retirement_age=beneficiary_record.normal_retirement_age, 
			early_retirement_age=beneficiary_record.earliest_retirement_age)
		detail_record.early_retirement_reduction_instructions.append(
			Instruction(description='Get respondent\'s early retirement reduction',
				expressions=[f'respondent\'s early retirement reduction = {percentage(respondent.early_retirement_reduction)}']))
		detail_record.early_retirement_reduction_instructions.append(
			Instruction(description='Cap Delay Retirement Credit', 
				expressions=[
					'early retirement reduction = min(max early retirement reduction, respondent\'s early retirement reduction',
					f'early retirement reduction = min({percentage(beneficiary_record.max_early_retirement_reduction)}, {percentage(respondent.early_retirement_reduction)})',
					f'early retirement reduction = {percentage(beneficiary_record.early_retirement_reduction)}']))
		detail_record.benefit_instructions = [
			Instruction(description='Get delay retirement credit', expressions=[f'delay retirement credit = {percentage(beneficiary_record.delay_retirement_credit)}']),
			Instruction(description='Get early retirement reduction', expressions=[f'early retirement reduction = {percentage(beneficiary_record.early_retirement_reduction)}']),
			Instruction(description='Get primary insurance amount', expressions=[f'primary insurance amount = {beneficiary_record.final_primary_insurance_amount}']),
			Instruction(description='Calculate benefit', expressions=[
				'benefit = primary insurance amount x (1 + (delay retirement credit + early retirement reduction))',
				f'benefit = {beneficiary_record.final_primary_insurance_amount} x (1 + ({percentage(beneficiary_record.delay_retirement_credit)} + {percentage(beneficiary_record.early_retirement_reduction)}))',
				f'benefit = {beneficiary_record.final_primary_insurance_amount} x {percentage(1 + (beneficiary_record.delay_retirement_credit + beneficiary_record.early_retirement_reduction))}',
				f'benefit = {beneficiary_record.benefit}'])]
		return detail_record

	def getDependentBenefitsInstructions(self, benefit_rules, beneficiary_record, spousal_beneficiary_record, detail_record):
		detail_record.spousal_insurance_benefit_instructions = benefit_rules.spousal_insurance_benefit_law.stepByStep(
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount,
			government_pension_offset=beneficiary_record.government_pension_offset)
		return detail_record

	def getSurvivorBenefitsInstructions(self, benefit_rules, respondent, beneficiary_record, spousal_beneficiary_record, detail_record):
		detail_record.survivor_insurance_benefit_instructions = benefit_rules.survivor_insurance_benefit_law.stepByStep(
			primary_insurance_amount=beneficiary_record.benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=respondent.survivor_early_retirement_reduction, 
			spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
			government_pension_offset=beneficiary_record.government_pension_offset)
		return detail_record