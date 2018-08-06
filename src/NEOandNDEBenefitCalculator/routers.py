from rest_framework.routers import SimpleRouter
from NEOandNDEBenefitCalculator.views import *

NEONDERouter = SimpleRouter()
NEONDERouter.register(r'', CalculatorViewSet, 'neonde')
NEONDERouter.register(r'respondents', RespondentViewSet, 'respondents')
NEONDERouter.register(r'records', RecordViewSet, 'records')