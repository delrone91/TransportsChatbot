#!/bin/bash
# Lance le backend Flask depuis le bon répertoire
cd "$(dirname "$0")"
exec chatbot/bin/python3 app.py
