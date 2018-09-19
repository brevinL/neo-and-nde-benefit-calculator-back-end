from datetime import date
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import GovernmentPensionOffset, Money, Task

class GovernmentPensionOffsetTestCase(TestCase):
	def setUp(self):
		GovernmentPensionOffset.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)

	def test_calculate(self):
		gpo = GovernmentPensionOffset.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(600 * 2/3, gpo.calculate(monthly_non_covered_pension=Money(amount=600)))

	def test_stepByStep(self):
		gpo = GovernmentPensionOffset.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		
		expected_task = Task.objects.create()
		instruction = expected_task.instruction_set.create(description='Get monthly non covered pension', order=1)
		instruction.expression_set.create(description='monthly non covered pension = $600.00', order=1)
		instruction = expected_task.instruction_set.create(description='Get offset', order=2)
		instruction.expression_set.create(description='offset = 2/3', order=1)
		instruction = expected_task.instruction_set.create(description='Multiply the monthly non covered pension with the offset', order=3)
		instruction.expression_set.create(description='government pension offset = monthly non covered pension x offset', order=1)
		instruction.expression_set.create(description='government pension offset = $600.00 x 2/3', order=2)
		instruction.expression_set.create(description='government pension offset = $400.00', order=3)

		self.assertEqual(expected_task, gpo.stepByStep(monthly_non_covered_pension=Money(amount=600)))

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.reverse import reverse
from BenefitRule.views import GovernmentPensionOffsetViewSet
from BenefitRule.serializers import MoneySerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient
class GovernmentPensionOffsetAPITestCase(APITestCase):
	def setUp(self):
		GovernmentPensionOffset.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)

	# https://stackoverflow.com/questions/30992377/django-test-requestfactory-vs-client
	def test_calculate(self):
		gpo = GovernmentPensionOffset.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31))

		monthly_non_covered_pension = Money(amount=600)

		client = APIClient()
		url = reverse('benefit-rule:government-pension-offset-calculate', args=[gpo.id])
		serializer = MoneySerializer(monthly_non_covered_pension)
		response = client.post(url, {'monthly_non_covered_pension': {'amount': 600.00}}, format='json') 
		# gpo_rule_calculate_view = GovernmentPensionOffsetViewSet.as_view({'post': 'calculate'})
		# response = gpo_rule_calculate_view(request)

		print(response.data)
		serializer = MoneySerializer(response.data)
		# print(serializer.data)
		# print(gpo.calculate(monthly_non_covered_pension=monthly_non_covered_pension))
		# self.assertEqual(serializer.data, gpo.calculate(monthly_non_covered_pension=monthly_non_covered_pension))