#!/usr/bin/bash
#in future set the venv
uvicorn main:app --workers 3 --reload --port 8000
