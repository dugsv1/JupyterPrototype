@echo off
start cmd.exe /k cd /d "%~dp0"
echo conda activate JupyterPrototype> clipboard.txt
echo jupyter notebook >> clipboard.txt
type clipboard.txt | clip
del clipboard.txt
