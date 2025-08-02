#!/bin/bash
python3 -m venv env
source env/bin/activate 
pip3 install -r requirements.txt
mkdir -p yomocoin_logs
mkdir -p yomocoin_backups
python3 george.py
