#!/bin/bash
echo "========================================"
echo " TikTok AI Video Generator - Backend"
echo "========================================"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[!] Archivo .env creado. Edita tus API keys."
fi
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
