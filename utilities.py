import logging
import psutil
import warnings
import os

# Adjust based on your server RAM constraints
CHUNK_SIZE = 10000

# Configure logging
logging.basicConfig(filename=os.environ.get('LOG_FILE_PATH', "'script.log'"), level=logging.DEBUG)
# Suppress the SQLAlchemy warning that arises when generating .geojson
warnings.filterwarnings('ignore', 'pandas only supports SQLAlchemy connectable')

def check_ram_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss
