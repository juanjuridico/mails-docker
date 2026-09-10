#!/bin/bash
# Script para ejecutar pruebas localmente

echo "Ejecutando pruebas unitarias..."
pytest tests/ -v --tb=short
