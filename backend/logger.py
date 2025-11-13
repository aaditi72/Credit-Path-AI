import logging
from datetime import datetime
from pathlib import Path
import json

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "requests.log"

# Configure logging system
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_request(data: dict, result: dict):
    """
    Logs incoming request and outgoing prediction result in structured JSON format.
    """

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "request_data": data,
        "response_data": result
    }

    logging.info(json.dumps(log_entry, indent=2))
