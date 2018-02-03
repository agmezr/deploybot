#!/bin/bash
if [[ -e venv ]]; then
  source venv/bin/activate
fi

python __init__.py
