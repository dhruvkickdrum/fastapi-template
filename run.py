#!/usr/bin/env python3
"""
Application entrypoint.
Run with:  python run.py
"""
import socket

import uvicorn

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


def _is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _pick_port(host: str, preferred_port: int, attempts: int = 10) -> int:
    for port in range(preferred_port, preferred_port + attempts):
        if _is_port_available(host, port):
            return port
    raise RuntimeError(
        f"No free port found in range {preferred_port}-{preferred_port + attempts - 1}"
    )

if __name__ == "__main__":
    setup_logging()
    port = _pick_port(settings.HOST, settings.PORT)
    if port != settings.PORT:
        logger.warning(
            "Configured port is busy; using fallback port",
            extra={"configured_port": settings.PORT, "selected_port": port},
        )

    uvicorn_kwargs = {
        "host": settings.HOST,
        "port": port,
        "reload": settings.DEBUG,
        "log_config": None,  # we manage logging ourselves
    }

    if settings.DEBUG:
        uvicorn_kwargs["reload_excludes"] = [
            "logs/*",
            "logs",
            "htmlcov/*",
            "htmlcov",
            ".pytest_cache/*",
            ".pytest_cache",
            "__pycache__/*",
            "__pycache__",
        ]

    uvicorn.run("app.main:app", **uvicorn_kwargs)
