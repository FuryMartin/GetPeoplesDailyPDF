@echo off
python rmrb_paper.py
TIMEOUT /T 120
cd ..
cd ./temp
del *.pdf