from rest_framework.routers import SimpleRouter
from NEOandNDEBenefitCalculator.views import *

NEONDERouter = SimpleRouter()

NEONDERouter.register(r'respondent', RespondentViewSet, 'respondent')
NEONDERouter.register(r'record', RecordViewSet, 'record')
NEONDERouter.register(r'detail-record', DetailRecordViewSet, 'detail-record')