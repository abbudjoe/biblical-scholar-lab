from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import uvicorn

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tests"))

from test_vs01_study_workspace import synthetic_archive  # noqa: E402

from bsl.interfaces.vs01_web import create_vs01_web_app  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="bsl-vs01-web-") as temporary:
        archive_root = synthetic_archive.__wrapped__(Path(temporary).resolve())
        app = create_vs01_web_app(archive_root, ROOT / "web/dist")
        uvicorn.run(app, host="127.0.0.1", port=args.port, workers=1, reload=False, access_log=False)


if __name__ == "__main__":
    main()
