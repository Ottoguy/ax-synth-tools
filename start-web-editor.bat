@echo off
rem AX-Synth Web Editor: serves web\ on http://localhost:8765 and opens it in Microsoft Edge.
rem Close MIDI-OX, the Roland Editor and the Librarian first (only one program can use the synth's USB port).
cd /d "%~dp0"
py -3 web\serve.py 8765 --edge
if errorlevel 1 pause
