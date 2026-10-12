"""Render the class and data-flow diagrams used in the Review 2 deck (PlantUML through kroki.io).

    py presentation/make_review2_diagrams.py

Same content as gen_diagrams.py in the project root, laid out for a slide:
higher resolution, and the class diagram runs left to right so its text stays
readable. Writes review2_class_diagram.png and review2_data_flow.png here.
"""
import base64
import os
import urllib.request
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))

STYLE = '''
skinparam dpi 200
skinparam shadowing false
skinparam defaultFontName Arial
skinparam defaultFontSize 13
skinparam ArrowColor #6B7A90
skinparam roundCorner 8
'''

CLASS_DIAGRAM = '''@startuml
''' + STYLE + '''
skinparam classAttributeIconSize 0
skinparam class {
  BackgroundColor #EEF3FA
  BorderColor #2A78D6
  FontColor #1B2A41
  AttributeFontColor #4A5568
}
left to right direction
hide empty members

class Orchestrator {
  + optimize(program)
}
class CodeAnalyzer {
  + analyze(program)
}
class OptimizationSpecialist {
  + mode: rule | hybrid | llm
  + route(program, opportunities)
  + propose(program, decision)
}
class RuleBasedOptimizer {
  + propose(program, opportunity)
}
abstract class BaseLLMOptimizer {
  + propose(program)
}
class GeminiOptimizer
class GroqOptimizer
class OllamaOptimizer
class Verifier {
  + verify(original, candidate)
}
class CostEvaluator {
  + evaluate(program)
}
class DecisionLogger {
  + log_route()
  + log_accept()
  + log_reject()
}

Orchestrator *-- CodeAnalyzer
Orchestrator *-- OptimizationSpecialist
Orchestrator *-- Verifier
Orchestrator *-- CostEvaluator
Orchestrator --> DecisionLogger
OptimizationSpecialist *-- RuleBasedOptimizer
OptimizationSpecialist o-- BaseLLMOptimizer
BaseLLMOptimizer <|-- GeminiOptimizer
BaseLLMOptimizer <|-- GroqOptimizer
BaseLLMOptimizer <|-- OllamaOptimizer
@enduml'''

DATA_FLOW = '''@startuml
''' + STYLE + '''
skinparam rectangle {
  BackgroundColor #FFFFFF
  BorderColor #6B7A90
  FontColor #1B2A41
}
skinparam usecase {
  BackgroundColor #EEF3FA
  BorderColor #2A78D6
  FontColor #1B2A41
}
skinparam database {
  BackgroundColor #FFFFFF
  BorderColor #0B8A0B
  FontColor #1B2A41
}

database "Source code\\n(.src / .c)" as src
rectangle "Front end" {
  usecase "Lexer" as lex
  usecase "Parser" as parse
  usecase "TAC Generator" as tacgen
}
database "TAC program" as tac
rectangle "Agent loop (Orchestrator)" {
  usecase "Code Analyzer" as analyzer
  usecase "Optimization Specialist\\n(routes each step)" as specialist
  usecase "Rule-based Optimizer" as rules
  usecase "LLM Optimizer\\n(Gemini / Groq / Ollama)" as llm
  usecase "Verifier" as verifier
  usecase "Cost Evaluator" as cost
}
database "Logs, metrics,\\ncharts" as out

src --> lex
lex -> parse : tokens
parse -> tacgen : AST
tacgen --> tac : TAC
tac --> analyzer
analyzer -> specialist : opportunities
specialist --> rules : Option A
specialist --> llm : Option B
rules --> verifier : candidate
llm --> verifier : candidate
verifier -> cost : verified
cost -> tac : accept and update
cost --> out : every decision
@enduml'''


def render(source: str, filename: str, folder: str = HERE) -> None:
    encoded = base64.urlsafe_b64encode(zlib.compress(source.encode("utf-8"), 9)).decode("ascii")
    request = urllib.request.Request(f"https://kroki.io/plantuml/png/{encoded}", headers={"User-Agent": "Mozilla/5.0"})
    path = os.path.join(folder, filename)
    with urllib.request.urlopen(request, timeout=60) as response, open(path, "wb") as fh:
        fh.write(response.read())
    print("saved", path)


if __name__ == "__main__":
    render(CLASS_DIAGRAM, "review2_class_diagram.png")
    render(DATA_FLOW, "review2_data_flow.png")
