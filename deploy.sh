#!/bin/bash
source .venv/bin/activate || python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt &&
modal run a1111_modal_worker/download.py &&
modal deploy a1111_modal_worker/server.py
