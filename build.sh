#!/bin/bash
black .
pip-compile --output-file=- > requirements.txt