import os 
from dotenv import load_dotenv

load_dotenv()


class Setting:
    '''Setting up environ variables'''
    def __init__(self):
        # JWT-Related Config
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
        self.ACCESS_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        self.REFRESH_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

        # Frontend URL
        self.FRONTEND_URL = os.getenv("FRONTEND_URL")

        # Rate Limiter Config


setting = Setting()