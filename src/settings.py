import os
import dotenv

dotenv.load_dotenv()

# Capashino
local_work = False

if local_work is True:
    CAPASHINO_BASE_URL = os.getenv("CAPASHINO_BASE_URL_LOCAL")
else:
    CAPASHINO_BASE_URL = os.getenv("CAPASHINO_BASE_URL")

CAPASHINO_API_KEY = os.getenv("CAPASHINO_API_KEY")

# PostgreSQL
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING")

# Kafka
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
