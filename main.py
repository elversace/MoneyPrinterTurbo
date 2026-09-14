import os

import uvicorn
from loguru import logger

from app.config import config

if __name__ == "__main__":
    listen_host = os.getenv("MPT_LISTEN_HOST", config.listen_host)
    listen_port = int(os.getenv("MPT_LISTEN_PORT", str(config.listen_port)))

    logger.info(
        "start server, docs: http://127.0.0.1:" + str(listen_port) + "/docs"
    )
    # FFmpeg probing is handled in the shared task pipeline.
    uvicorn.run(
        app="app.asgi:app",
        host=listen_host,
        port=listen_port,
        reload=config.reload_debug,
        log_level="warning",
    )
