@echo off
rem Offline demo: optimize one C program with the local Ollama model (no internet, no API key).
rem
rem   ollama_demo.bat                                  the sample written for the local model
rem   ollama_demo.bat demo_programs\3_loop.c           any other C file
rem   ollama_demo.bat my_program.c --inputs n=5        extra demo.py options go after the file
rem   ollama_demo.bat --llm-first                      ask the model before the rules (more LLM steps to watch)
rem
rem The model runs on the GPU when Ollama can use it, otherwise on the CPU (slower).
rem To keep the laptop cool on the CPU, limit the threads first:   set OLLAMA_NUM_THREAD=6
setlocal
cd /d "%~dp0"

ollama list >nul 2>&1
if errorlevel 1 (
    echo Ollama is not running. Start the Ollama app ^(or run "ollama serve" in another window^) and try again.
    exit /b 1
)
ollama list | findstr /i "qwen2.5-coder" >nul
if errorlevel 1 (
    echo The model is not downloaded yet. Run:  ollama pull qwen2.5-coder:7b
    exit /b 1
)

set "ROUTE="
if /i "%~1"=="--llm-first" (
    set "ROUTE=--optimizer llm"
    shift
)
if "%~1"=="" (
    py demo.py demo_programs\6_ollama_offline.c --offline %ROUTE%
) else (
    py demo.py %1 %2 %3 %4 %5 %6 %7 %8 %9 --offline %ROUTE%
)
endlocal
