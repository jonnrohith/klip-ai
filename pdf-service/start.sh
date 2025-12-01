#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/opt/libffi/lib/pkgconfig:$PKG_CONFIG_PATH"
uvicorn main:app --port 8002 --reload

