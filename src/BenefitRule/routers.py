from rest_framework.routers import SimpleRouter
from BenefitRule.views import *

BenefitRuleRouter = SimpleRouter()
BenefitRuleRouter.register(r'relationship', RelationshipViewSet, 'relationship')
