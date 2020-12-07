from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.flaskenv'), override=True)
load_dotenv(find_dotenv('.env'), override=True)

from web import create_app

app = create_app()
