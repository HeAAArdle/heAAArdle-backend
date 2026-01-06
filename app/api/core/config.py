from dotenv import load_dotenv
import os

# reads .env so we can use os.getenv to get environment variables from it
load_dotenv()

# get the environment variable ENV and default to "development" if not set
ENV = os.getenv("ENV", "development")