@echo off
rem Procedural Prompting -- the installer for Windows: double-click it, or run it from a terminal with its options.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
if errorlevel 1 pause
