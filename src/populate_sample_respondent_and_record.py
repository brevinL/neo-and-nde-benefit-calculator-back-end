import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BenefitCalculator.settings')
django.setup()
from BenefitRule.models import Relationship
from NEOandNDEBenefitCalculator.models import Money, Respondent
from django.contrib.sites.models import Site

# Start execution here!
if __name__ == '__main__':
	print("Starting Respondent & Record population script...")

	beneficary = Respondent.objects.create(
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

	spouse = Respondent.objects.create(
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

	Relationship.objects.create(
		content_object1=beneficary, 
		content_object2=spouse, 
		person1_role=Relationship.BENEFICIARY,
		person2_role=Relationship.SPOUSE,
		relationship_type=Relationship.MARRIED)

	import urllib.request
	url = f"http://localhost:8000/api/neo-and-nde-benefit-calculator/record/summary/?respondent={beneficary.id}"
	'https://%s%s' % (Site.objects.get_current().domain, reverse('neo-and-nde-benefit-calculator:respondent-list'))
	contents = urllib.request.urlopen(url).read()

	print("Finish Respondent & Record population script.")