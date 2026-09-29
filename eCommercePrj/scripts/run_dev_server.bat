@echo off
cd /d "%~dp0.."
"..\myEcommerceWorld\Scripts\python.exe" manage.py runserver 8000
