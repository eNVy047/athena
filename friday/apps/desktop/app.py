import logging
import time
from dotenv import load_dotenv

# Load environment variables FIRST — before any provider or kernel import reads os.getenv()
load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("friday.desktop")

from friday.apps.desktop.application import DesktopApplication

def main():
    t0 = time.time()
    logger.info("F.R.I.D.A.Y. Desktop starting...")
    app = DesktopApplication()
    logger.info(f"Desktop initialized in {(time.time() - t0)*1000:.0f}ms")
    app.run()

if __name__ == "__main__":
    main()
