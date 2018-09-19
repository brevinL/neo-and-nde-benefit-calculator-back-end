from datetime import date
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action 
from rest_framework.response import Response
from BenefitRule.models import BenefitRule, Relationship, Record, DetailRecord, Person
from BenefitRule.serializers import DetailRecordSerializer

# todo: extend records models, viewset, and serializer
class DetailRecordViewSet(viewsets.ModelViewSet):
	queryset = DetailRecord.objects.all()
	serializer_class = DetailRecordSerializer

	def get_benefit_rules(self, start_date, end_date):
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except BenefitRule.DoesNotExist:
			benefit_rules = None
		return benefit_rules

	def get_beneficary(self, id):
		return Person.objects.get(id=id)

	def get_record(self, person):
		try:
			record = self.objects.get(person=person)
		except Record.DoesNotExist:
			record = None
		return record

	def get_detail_record(self, person):
		try:
			detail_record = self.detail_record_class.objects.get(person=person)
		except self.detail_record_class.DoesNotExist:
			detail_record = self.detail_record_class(content_object=person)
			detail_record.save()
		return detail_record

	@action(methods=['get'], detail=False)
	def update_detail_record(self, request, pk=None):
		# query = BenefitRule.objects.aggregate(Max('start_date'), Max('end_date'))
		year = 2016
		benefit_rules = self.get_benefit_rules(start_date=date(year, 1, 1), end_date=date(year, 12, 31))
		if benefit_rules is None:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		beneficary = self.get_beneficary()

		record = self.get_record(person=beneficary)
		if record is None:
			return Response({'detail': 'No Record match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		detail_record = self.get_detail_record(person=beneficary)
		detail_record = detail_record.calculate_retirement_record(benefit_rules=benefit_rules, beneficiary_record=record)

		respondent_married_relationships = Relationship.objects.filter(Q(person1=person) | Q(person2=person), relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=person)
			spouse_record = self.get_record(person=spouse)
			if spouse_record is None:
				return Response({'detail': 'No Record match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

			spouse_detail_record = self.get_detail_record(person=spouse)
			spouse_detail_record = spouse_detail_record.calculate_retirement_record(benefit_rules=benefit_rules, beneficiary_record=record)

			detail_record = detail_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)
			detail_record = detail_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)

			spouse_detail_record = spouse_detail_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)
			spouse_detail_record = spouse_detail_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)

		record_serializer = DetailRecordSerializer(instance=detail_record, context={'request': request})
		return Response(record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)