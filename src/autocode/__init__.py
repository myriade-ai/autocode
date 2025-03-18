import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Silence some overly verbose loggers
logging.getLogger("PIL").setLevel(logging.WARNING)

from .code_editor import *
from .code_editor_utils import *
from .terminal import *
