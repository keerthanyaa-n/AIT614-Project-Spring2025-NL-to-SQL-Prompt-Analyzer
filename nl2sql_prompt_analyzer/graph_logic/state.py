# graph_logic/state.py
from typing import TypedDict, Optional, Dict, Any

class GraphState(TypedDict):
    """Defines the structure for data passed between graph nodes."""
    nl_query: str
    prompt_strategy: str
    llm_config: str # Identifier for the selected LLM
    dataset_context: Optional[Dict[str, Any]] # For schema, examples etc.
    final_prompt: Optional[str] # The prompt sent to the LLM
    generated_sql: Optional[str] # The SQL output from the LLM
    error: Optional[str] # To capture any errors during execution