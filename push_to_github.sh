#!/bin/bash
# Script para subir a GitHub

echo "Inicializando repositorio Git..."
git init

echo "Añadiendo archivos..."
git add .

echo "Haciendo commit..."
git commit -m "Proyecto mails-docker completo con TempMailG + Selenium"

echo "Configurando remote..."
git remote add origin https://github.com/juanjuridico/mails-docker.git

echo "Subiendo a GitHub..."
git push -u origin main

echo "Proyecto subido a: https://github.com/juanjuridico/mails-docker"
