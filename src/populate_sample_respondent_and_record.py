import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BenefitCalculator.settings')
django.setup()
from BenefitRule.models import Relationship
from NEOandNDEBenefitCalculator.models import Money, Respondent
from rest_framework.reverse import reverse

# Start execution here!
if __name__ == '__main__':
	print("Starting Respondent & Record population script...")

	beneficary, created = Respondent.objects.get_or_create(
		year_of_birth=1954,
		years_of_covered_earnings=15,
		annual_covered_earning=Money.objects.create(amount=30000.00),
		years_of_non_covered_earnings=25,
		annual_non_covered_earning=Money.objects.create(amount=40000.00),
		fraction_of_non_covered_aime_to_non_covered_pension=0.67,
		early_retirement_reduction=0.00,
		delay_retirement_credit=0.00,
		spousal_early_retirement_reduction=0.00,
		survivor_early_retirement_reduction=0.00)

	spouse, created = Respondent.objects.get_or_create(
		year_of_birth=1954,
		years_of_covered_earnings=40,
		annual_covered_earning=Money.objects.create(amount=50000.00),
		years_of_non_covered_earnings=0,
		annual_non_covered_earning=Money.objects.create(amount=0.00),
		fraction_of_non_covered_aime_to_non_covered_pension=0.67,
		early_retirement_reduction=0.00,
		delay_retirement_credit=0.00,
		spousal_early_retirement_reduction=0.00,
		survivor_early_retirement_reduction=0.00)

	relationship, created = Relationship.objects.get_or_create(
		content_object1=beneficary, 
		content_object2=spouse, 
		person1_role=Relationship.BENEFICIARY,
		person2_role=Relationship.SPOUSE,
		relationship_type=Relationship.MARRIED)

	# import argparse
	# parser = argparse.ArgumentParser(description='Populate a sample respondent and respondent\'s spouse. Also, calls on update record and detail record API.')
	# parser.add_argument('integers', metavar='N', type=int, nargs='+',
	# 	help='an integer for the accumulator')
	# parser.add_argument('--sum', dest='accumulate', action='store_const',
	# 	const=sum, default=max,
	# 	help='sum the integers (default: find the max)')

	import urllib.request

	domain = 'localhost:8000' # Site.objects.get_current().domain
	path = reverse('neo-and-nde-benefit-calculator:respondent-detail', args=[beneficary.id])
	action = 'update_record/'
	url = f"http://{domain}{path}{action}"
	print(url)
	contents = urllib.request.urlopen(url).read()
	print(contents)

	action = 'update_detail_record/'
	url = f"http://{domain}{path}{action}"
	print(url)
	contents = urllib.request.urlopen(url).read()
	print(contents)

	print("Finish Respondent & Record population script.")