import logging
import os
import sys

# 10ks char = 250 lines => 2500 tokens
os.environ["AUTOCHAT_OUTPUT_SIZE_LIMIT"] = "10_000"

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Silence some overly verbose loggers
logging.getLogger("PIL").setLevel(logging.WARNING)


from .code_editor import *  # noqa: E402, F403
from .code_editor_utils import *  # noqa: E402, F403
from .terminal import *  # noqa: E402, F403
