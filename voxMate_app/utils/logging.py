# Required python imports
import logging
from ctypes import *
from dotenv import load_dotenv


# ================= INITIALIZATION =================
#Load env
load_dotenv('../../.env')

# Setup logging with more detailed format

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/smart_speaker.log')
    ]
)
logger = logging.getLogger(__name__)
