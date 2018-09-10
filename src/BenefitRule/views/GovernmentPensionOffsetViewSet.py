from rest_framework import viewsets
from rest_framework.decorators import action
from BenefitRule.models import GovernmentPensionOffset
from BenefitRule.serializers import TaskSerializer, MoneySerializer, GovernmentPensionOffsetSerializer

class GovernmentPensionOffsetViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = GovernmentPensionOffset.objects.all()
	serializer_class = GovernmentPensionOffsetSerializer

	# need to be able to handle record id or request record
	@action(methods=['get'], detail=False)
	def calculate(self, request):
		record_id = request.query_params.get('record', None)
		record = get_object_or_404(Record, id=record_id)

		year = 2016
		gpo_rule = get_object_or_404(GovernmentPensionOffset, start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		gpo = gpo_rule.calculate(monthly_non_covered_pension=record.monthly_non_covered_pension)

		gpo_serializer = MoneySerializer(gpo)
		return Response(gpo_serializer.data, content_type='application/json;charset=utf-8')

	@action(methods=['get'], detail=False)
	def stepByStep(self, request):
		record_id = request.query_params.get('record', None)
		try:
			record = Record.objects.get(id=record_id)
		except Record.DoesNotExist:
			raise Http404("No Record matches the given query.")

		year = 2016
		try:
			gpo_rule = GovernmentPensionOffset.objects.get(start_date__lte=date(year, 1, 1), end_date__gte=date(year, 12, 31))
		except GovernmentPensionOffset.DoesNotExist:
			raise Http404("No GovernmentPensionOffset matches the given query.")
		gpo_task = gpo_rule.stepByStep(monthly_non_covered_pension=record.monthly_non_covered_pension)

		gpo_serializer = TaskSerializer(gpo_task)
		return Response(gpo_serializer.data, content_type='application/json;charset=utf-8')