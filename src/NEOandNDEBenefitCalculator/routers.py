from rest_framework.routers import SimpleRouter
from NEOandNDEBenefitCalculator.views import NEONDEView

NEONDERouter = SimpleRouter()
NEONDERouter.register(r'', NEONDEView, 'neonde')