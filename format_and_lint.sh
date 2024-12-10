#!/bin/bash

echo "Running Black formatter..."
black src/

echo -e "\nRunning isort import sorter..."
isort src/

echo -e "\nRunning flake8 linter..."
flake8 src/

echo -e "\nRunning pytest..."
pytest tests/ -v --cov=src
