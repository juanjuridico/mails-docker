#!/bin/bash
set -e
echo "Ejecutando pruebas..."
python -m pytest tests/ -v --tb=short
