---
name: video-analizador
description: Analiza un video: transcribe el audio (faster-whisper) y lee el texto en pantalla (Tesseract OCR), con marcas de tiempo y salida TXT/JSON/SRT/VTT. Prioriza español.
---
# video-analizador
Comando: `video_analizador video.mp4 [-o carpeta] [--lang es|en|auto] [--model small|medium|large-v3] [--offline]`
Requisitos: ffmpeg, tesseract-ocr (+spa), venv con faster-whisper, pytesseract, opencv-python-headless.
Instalación: ver `/opt/video_analizador/README.md`. Script fuente: `scripts/video_analizador.py`.
Pendiente: el modelo Whisper requiere acceso a huggingface.co (bloqueado en el entorno actual).
