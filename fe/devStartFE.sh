#!/usr/bin/bash
/home/sharsha/pyvirt/fe/bin/gunicorn --reload --workers 3 --bind unix:ptff.sock -m 007 wsgi:app  