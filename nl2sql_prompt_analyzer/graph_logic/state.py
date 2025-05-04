# graph_logic/state.py

# --- Typing Imports ---
from typing import TypedDict, Optional, Dict, Any, List

# --- State Definition ---
class GraphState(TypedDict):
    """
    Defines the structure for data passed between graph nodes.
    Keys represent pieces of information accumulated during the graph run.
    """
    # Inputs
    nl_query: str
    prompt_strategy: str
    llm_config: str # Identifier for the main SQL generation LLM
    dataset_name: Optional[str]

    # Intermediate results for structured path
    all_tables_names_descs: Optional[List[Dict[str, str]]] # List of dicts {name: ..., description: ...}
    prediction_prompt: Optional[str] # <<< RE-ADDED: Prompt specifically for predicting relevant tables
    relevant_table_names: Optional[List[str]]
    relevant_schema_metadata: Optional[Dict[str, Any]] # Stores schema dicts for relevant tables

    # General intermediate results
    final_prompt: Optional[str] # The prompt sent to the main SQL generation LLM

    # Outputs / Errors
    generated_sql: Optional[str]
    error: Optional[str]

