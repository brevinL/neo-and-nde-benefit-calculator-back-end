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

	@action(methods=['get'], detail=False)
	def update_record(self, request, pk=None):
		year = 2016
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except BenefitRule.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		if True:
			person = Person.objects.get(request)
		else:
			respondent = Respondent.objects.get(request)
			
		record = self.get_object()
		try:
			record = self.objects.get(person=person)
		except self.record_class.DoesNotExist:
			record = self.record_class(content_object=person)
			record.save()
		record = record.calculate_retirement_record(benefit_rules=benefit_rules)

		respondent_married_relationships = Relationship.objects.filter(Q(person1=person) | Q(person2=person), relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=person)
			try:
				spouse_record = self.record_class.objects.get(person=spouse)
			except self.record_class.DoesNotExist:
				spouse_record = self.record_class(content_object=spouse)
				spouse_record.save()
			spouse_record = spouse_record.calculate_retirement_record(benefit_rules=benefit_rules)

			record = record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
			record = record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record)
			
			spouse_record = spouse_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record)
			spouse_record = spouse_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record)

		record_serializer = RecordSerializer(record, context={'request': request})
		return Response(record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)