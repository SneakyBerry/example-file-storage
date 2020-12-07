import argparse
import logging

from aiohttp import web
from file_storage.app import get_application

logging.basicConfig(
    format="[%(asctime)s][%(levelname)s][%(name)s]: %(msg)s",
    level=logging.INFO,
)


def run(port: int) -> None:
    """Run application."""
    app = get_application()
    web.run_app(app, port=port)


def cli():
    """Command line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        help="Port where server will be serving his master",
        type=int,
        default=8080,
    )
    args = parser.parse_args()
    run(port=args.port)


if __name__ == "__main__":
    cli()
