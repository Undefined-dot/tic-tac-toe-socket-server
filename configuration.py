import os
from dotenv import load_dotenv

BACKEND_URL = os.environ.get('BACKEND_URL', None)
FRONTEND_URL= os.environ.get('FRONTEND_URL','relou.app')