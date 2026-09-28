@echo off
rem AX-Synth Web Editor (Windows): double-click to start.
rem Runs a small local web server with the PowerShell built into Windows (nothing to install)
rem and opens the editor in Microsoft Edge. Keep the window open while you use it; close it to stop.
rem Close any other program that uses the synth first (only one program at a time can use its USB port).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve.ps1" -Port 8765
if errorlevel 1 pause
