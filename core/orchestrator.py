import logging
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.errors import GraphInterrupt
from langgraph.checkpoint.memory import MemorySaver
from core.brain import OllamaBrain

# Configuration logging
logger = logging.getLogger("bunshin.core.orchestrator")

# 1. État
class AgentState(TypedDict):
    query: str
    plan: str
    response: str
    verified: bool
    current_stage: int  
    current_model: str  
    errors: list
    burst_approved: bool 

STAGE_MODELS = {
    1: "qwen2.5-coder:1.5b",  
    2: "phi3:mini",          
    3: "qwen2.5-coder:32b"    
}

# 2. Nœuds
def initialization_node(state: AgentState) -> Dict[str, Any]:
    logger.info("--- [Nœud : Initialisation] ---")
    stage = state.get("current_stage", 1)
    return {
        "current_stage": stage,
        "current_model": STAGE_MODELS.get(stage, STAGE_MODELS[1]),
        "burst_approved": state.get("burst_approved", False),
        "errors": state.get("errors", [])
    }

def plan_node(state: AgentState) -> Dict[str, Any]:
    stage = state.get("current_stage", 1)
    model_name = STAGE_MODELS.get(stage, STAGE_MODELS[stage])
    
    if stage == 3:
        return {"plan": "[PLAN CLOUD] Exécution distante.", "current_model": model_name}
        
    brain = OllamaBrain()
    brain.model = model_name
    try:
        plan = brain.generate(f"Plan pour : {state['query']}", timeout=15)
        return {"plan": plan, "current_model": model_name}
    except Exception as e:
        return {"plan": "Échec planification", "errors": [str(e)]}

def execute_node(state: AgentState) -> Dict[str, Any]:
    stage = state.get("current_stage", 1)
    
    # Si le bouton rouge a été activé, on force le passage au Stage 3
    if state.get("burst_approved") and stage < 3:
        logger.info("⚡ Passage forcé au Stage 3 (Cloud)")
        return {"current_stage": 3, "current_model": STAGE_MODELS[3]}

    model_name = STAGE_MODELS.get(stage, STAGE_MODELS[stage])
    
    # Exécution Cloud
    if stage == 3:
        return {"response": f"[RÉPONSE CLOUD 32B] Réponse pour : {state['query']}", "current_model": model_name}

    # Exécution Locale (Qwen 1.5b ou Phi-3)
    brain = OllamaBrain()
    brain.model = model_name
    try:
        # Timeout 300s pour Phi-3 (stage 2), 15s pour Qwen (stage 1)
        timeout = 300 if stage == 2 else 15
        response = brain.generate(f"Réponds à : {state['query']}", timeout=timeout)
        return {"response": response, "current_model": model_name}
    except Exception as e:
        return {"response": "Échec d'exécution", "errors": [str(e)]}

def verify_node(state: AgentState) -> Dict[str, Any]:
    response = state.get("response", "")
    stage = state.get("current_stage", 1)
    is_valid = len(response) > 0 and "Échec" not in response
    
    next_stage = stage if is_valid else stage + 1
    return {"verified": is_valid, "current_stage": next_stage}

def human_validation_node(state: AgentState) -> Dict[str, Any]:
    # Interruption uniquement au Stage 3
    if state.get("current_stage") == 3 and not state.get("burst_approved"):
        logger.warning("🚨 [HITL] En attente de validation humaine pour le Cloud Bursting.")
        raise GraphInterrupt("Bouton rouge requis.")
    return {}

# 3. Assemblage
def create_bunshin_orchestrator():
    workflow = StateGraph(AgentState)
    workflow.add_node("initialization", initialization_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("human_validation", human_validation_node)
    
    workflow.set_entry_point("initialization")
    workflow.add_edge("initialization", "plan")
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "verify")
    
    # Routage conditionnel
    workflow.add_conditional_edges("verify", 
        lambda s: "human_check" if not s["verified"] else END,
        {"human_check": "human_validation", "end": END})
    
    # Après validation ou si on a déjà l'approbation, on boucle vers plan
    workflow.add_edge("human_validation", "plan")
    
    return workflow.compile(checkpointer=MemorySaver())

