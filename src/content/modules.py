from typing import List, Dict, Any, Optional

MODULE_1_STEPS = [
    {
        "id": 1,
        "text": "Olá! Eu sou o Rev, seu assistente de educação financeira para investidores iniciantes.",
        "mascot": "MascotHello"
    },
    {
        "id": 2,
        "text": "Aqui, você aprende, pratica e evolui para tomar decisões financeiras com mais confiança.",
        "mascot": "MascotPoint"
    },
    {
        "id": 3,
        "text": "Vamos dar início com os conceitos iniciais sobre investimentos!",
        "mascot": "MascotPlan"
    }
]

MODULES_DATA = {
    "modulo_1": {
        "id": "modulo_1",
        "title": "Ordem de Operações e Fundamentos",
        "description": "Controle de gastos, quitação de dívidas caras e reserva de emergência.",
        "steps": MODULE_1_STEPS
    }
}

def get_module_steps(module_id: str = "modulo_1") -> List[Dict[str, Any]]:
    mod = MODULES_DATA.get(module_id, MODULES_DATA["modulo_1"])
    return mod["steps"]

def get_module_info(module_id: str = "modulo_1") -> Optional[Dict[str, Any]]:
    return MODULES_DATA.get(module_id)
