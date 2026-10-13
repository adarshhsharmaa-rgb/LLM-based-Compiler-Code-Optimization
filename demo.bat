@echo off
rem Starts the demo. Without arguments it opens the menu: pick a program, then who proposes
rem (rules, Groq, Gemini, the local Ollama model, or all of them side by side) and the cost model.
rem
rem   demo.bat                                      the menu
rem   demo.bat demo_programs\3_loop.c --use-llm     any demo.py options
rem   demo.bat demo_programs\3_loop.c --compare     the rules and every ready LLM, side by side
setlocal
cd /d "%~dp0"
py demo.py %*
endlocal
