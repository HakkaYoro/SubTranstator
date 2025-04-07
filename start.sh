#!/bin/bash

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run SubTranslator CLI with passed arguments
python3 -m subtranslator.main "$@"
