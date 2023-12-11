from geochem_portal.app import create_app

from mangum import Mangum

app = create_app()
lambda_handler = Mangum(app)
