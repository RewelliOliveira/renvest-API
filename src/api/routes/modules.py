from typing import List
from fastapi import APIRouter
from src.schemas.modules import StepItem, ModuleResponse
from src.services.module_service import ModuleService

router = APIRouter(tags=["modules"])

@router.get("/steps", response_model=List[StepItem])
def get_default_steps():
    return ModuleService.get_steps("modulo_1")

@router.get("/modules/{module_id}/steps", response_model=List[StepItem])
def get_module_steps(module_id: str):
    return ModuleService.get_steps(module_id)

@router.get("/modules/{module_id}", response_model=ModuleResponse)
def get_module_detail(module_id: str):
    return ModuleService.get_module(module_id)
