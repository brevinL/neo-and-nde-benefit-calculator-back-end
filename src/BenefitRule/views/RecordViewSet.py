from datetime import date
from django.db.models import Q
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action 
from rest_framework.response import Response
from BenefitRule.models import BenefitRule, Relationship, Record, DetailRecord, Person
from BenefitRule.serializers import RecordSerializer, PersonSerializer, DetailRecordSerializer
from NEOandNDEBenefitCalculator.models import Respondent
from django.contrib.contenttypes.models import ContentType

class RecordViewSet(viewsets.ModelViewSet):
	queryset = Record.objects.all()
	serializer_class = RecordSerializer

	def get_benefit_rules(self, start_date, end_date):
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except BenefitRule.DoesNotExist:
			benefit_rules = None

		return benefit_rules

	def get_beneficary(self):
		return Person.objects.get()

	def get_record(self, person):
		try:
			record = self.objects.get(person=person)
		except Record.DoesNotExist:
			record = Record(content_object=person)
			record.save()
		return record

	@action(methods=['get'], detail=False)
	def update_record(self, request, pk=None):
		year = 2016
		benefit_rules = self.get_benefit_rules(start_date=date(year, 1, 1), end_date=date(year, 12, 31))
		if benefit_rules is None:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		beneficary = self.get_beneficary()
			
		record = self.get_record(person=beneficary)
		record = record.calculate_retirement_record(benefit_rules=benefit_rules)

		respondent_married_relationships = Relationship.objects.filter(Q(person1=person) | Q(person2=person), relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=person)
			spouse_record = self.get_record(person=spouse)
			spouse_record = spouse_record.calculate_retirement_record(benefit_rules=benefit_rules)

			record = record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
			record = record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
			
			spouse_record = spouse_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record)
			spouse_record = spouse_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record)

		record_serializer = RecordSerializer(record, context={'request': request})
		return Response(record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)