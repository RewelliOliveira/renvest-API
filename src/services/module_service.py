from typing import List, Optional
from src.content.modules import get_module_steps, get_module_info
from src.schemas.modules import StepItem, ModuleResponse

class ModuleService:
    @staticmethod
    def get_steps(module_id: str = "modulo_1") -> List[StepItem]:
        steps_data = get_module_steps(module_id)
        return [StepItem(**step) for step in steps_data]

    @staticmethod
    def get_module(module_id: str = "modulo_1") -> Optional[ModuleResponse]:
        data = get_module_info(module_id)
        if not data:
            data = get_module_info("modulo_1")
        return ModuleResponse(**data) if data else None
