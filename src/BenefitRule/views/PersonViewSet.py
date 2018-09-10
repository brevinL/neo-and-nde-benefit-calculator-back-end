from datetime import date
from django.db.models import Q
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action 
from rest_framework.response import Response
from BenefitRule.models import BenefitRule, Relationship, Record, DetailRecord, Person
from BenefitRule.serializers import RecordSerializer, PersonSerializer
from NEOandNDEBenefitCalculator.models import Respondent
from django.contrib.contenttypes.models import ContentType

# fix to able to post only
# redudant code just to reference a overrided record and detail record managers
# get instance of record to calculate records/benefits instead of managers
class PersonViewSet(viewsets.ModelViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer
	record_class = Record
	detail_record_class = DetailRecord

	@action(methods=['get'], detail=True)
	def get_record(self, request, pk=None): # given an inital record -> applied benefit rules to record -> update record
		# have to change manually each year because you got to 
		# add in the numbers for the other laws to db anyways
		year = 2016
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except BenefitRule.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		person = self.get_object()
		try:
			record = Record.objects.get(person=person)
		except Record.DoesNotExist:
			record = Record.objects.create(person=person)
		record = record.calculate_retirement_record(benefit_rules=benefit_rules)

		respondent_married_relationships = Relationship.objects.filter(Q(person1=person) | Q(person2=person), relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=person)
			try:
				spouse_record = self.record_class.objects.get(person=spouse)
			except self.record_class.DoesNotExist:
				spouse_record = self.record_class.objects.create(person=spouse)
			spouse_record = spouse_record.calculate_retirement_record(benefit_rules=benefit_rules, person=spouse)

			record = record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
			record = record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
			
			spouse_record = spouse_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record)
			spouse_record = spouse_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record)

		record_serializer = RecordSerializer(record)
		return Response(record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)

	@action(methods=['get'], detail=True)
	def get_detail_record(self, request, pk=None):
		year = 2016
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except BenefitRule.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		person = self.get_object()

		try:
			record = self.record_class.objects.get(person=person)
		except Record.DoesNotExist:
			return Response({'detail': 'No Record match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		detail_record = DetailRecord.objects.calculate_retirement_record(benefit_rules=benefit_rules, person=person, beneficiary_record=record)

		respondent_married_relationships = Relationship.objects.filter(Q(person1=person) | Q(person2=person), relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=person)
			spouse_record = get_object_or_404(Record, person=spouse)
			spouse_detail_record = DetailRecord.objects.calculate_retirement_record(benefit_rules=benefit_rules, person=spouse, beneficiary_record=record)

			detail_record = DetailRecord.objects.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)
			detail_record = DetailRecord.objects.calculate_survivor_benefits(benefit_rules=benefit_rules, person=person, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)

			spouse_detail_record = DetailRecord.objects.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)
			spouse_detail_record = DetailRecord.objects.calculate_survivor_benefits(benefit_rules=benefit_rules, person=person, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)

		record_serializer = DetailRecordSerializer(instance=detail_record)
		return Response(record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)