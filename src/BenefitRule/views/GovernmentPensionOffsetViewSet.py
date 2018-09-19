from datetime import date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from BenefitRule.models import GovernmentPensionOffset
from BenefitRule.serializers import TaskSerializer, MoneySerializer, GovernmentPensionOffsetSerializer

class GovernmentPensionOffsetViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = GovernmentPensionOffset.objects.all()
	serializer_class = GovernmentPensionOffsetSerializer

	# need to be able to handle record id or request record
	@action(methods=['post'], detail=True)
	def calculate(self, request, pk=None):
		monthly_non_covered_pension = request.data.get('monthly_non_covered_pension', None)
		if monthly_non_covered_pension is None:
			return Response({'detail': 'monthly_non_covered_pension cannot be found within the request'}, content_type='application/json;charset=utf-8', status=status.HTTP_400_BAD_REQUEST)

		serializer = MoneySerializer(data=monthly_non_covered_pension)
		if not serializer.is_valid():
			return Response({'detail': serializer.errors}, content_type='application/json;charset=utf-8', status=status.HTTP_400_BAD_REQUEST)

		monthly_non_covered_pension = serializer.create(validated_data=monthly_non_covered_pension)

		year = 2016
		try:
			gpo_rule = GovernmentPensionOffset.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except GovernmentPensionOffset.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)
		gpo = gpo_rule.calculate(monthly_non_covered_pension=monthly_non_covered_pension)

		gpo_serializer = MoneySerializer(gpo)
		return Response(gpo_serializer.data, content_type='application/json;charset=utf-8')

	@action(methods=['post'], detail=True)
	def stepByStep(self, request, pk=None):
		record_id = request.query_params.get('record', None)

		year = 2016
		try:
			gpo_rule = GovernmentPensionOffset.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except GovernmentPensionOffset.DoesNotExist:
			raise Http404("No GovernmentPensionOffset matches the given query.")
		gpo_task = gpo_rule.stepByStep(monthly_non_covered_pension=record.monthly_non_covered_pension)

		gpo_serializer = TaskSerializer(gpo_task)
		return Response(gpo_serializer.data, content_type='application/json;charset=utf-8')