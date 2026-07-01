@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."

if not exist output mkdir output
explorer "%~dp0..\output"
