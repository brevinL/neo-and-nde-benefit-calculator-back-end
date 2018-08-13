from datetime import date
from math import inf
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Q
from django.shortcuts import render, get_object_or_404
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import list_route, action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from BenefitRule.models import Person, Money, Relationship
from NEOandNDEBenefitCalculator.models import *
from NEOandNDEBenefitCalculator.serializers import *

class DetailRecordViewSet(viewsets.ModelViewSet):
	queryset = DetailRecord.objects.all()
	serializer_class = DetailRecordSerializer

	@action(methods=['get'], detail=False)
	def stepByStep(self, request): # given an inital record -> applied benefit rules to record -> update record
		# http://www.django-rest-framework.org/api-guide/serializers/#dealing-with-multiple-objects
		respondent_id = request.query_params.get('respondent', None)
		respondent = get_object_or_404(Respondent, id=respondent_id)
		# relationships = self.serializeRelationships(data=request.data.pop('relationships', []))

		# have to change manually each year because you got to 
		# add in the numbers for the other laws to db anyways
		year = 2016
		benefit_rules = get_object_or_404(BenefitRule, Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
		record = get_object_or_404(Record, person=respondent)
		detail_record = DetailRecord.objects.calculate_retirement_record(benefit_rules=benefit_rules, respondent=respondent, beneficiary_record=record)

		respondent_married_relationships = Relationship.objects.filter(Q(person1=respondent) | Q(person2=respondent), relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=respondent)
			spouse_record = get_object_or_404(Record, person=spouse)
			spouse_detail_record = DetailRecord.objects.calculate_retirement_record(benefit_rules=benefit_rules, respondent=spouse, beneficiary_record=record)

			detail_record = DetailRecord.objects.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)
			detail_record = DetailRecord.objects.calculate_survivor_benefits(benefit_rules=benefit_rules, respondent=respondent, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)

			spouse_detail_record = DetailRecord.objects.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)
			spouse_detail_record = DetailRecord.objects.calculate_survivor_benefits(benefit_rules=benefit_rules, respondent=respondent, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)

		record_serializer = DetailRecordSerializer(instance=detail_record)
		return Response(record_serializer.data, content_type='application/json;charset=utf-8')