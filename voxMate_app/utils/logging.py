# Required python imports
import logging
from dotenv import load_dotenv


# Load env
load_dotenv("../../.env")

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    # Define the format with alignment
    format="%(asctime)s - %(filename)15s:%(lineno)5d - %(levelname)-8s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/home/hutch/voxMate/logs/voxMate_app.log"),
    ],
)
logger = logging.getLogger(__name__)
