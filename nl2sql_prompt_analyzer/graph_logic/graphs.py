# graph_logic/graph.py
# ... (Imports remain the same, but might need to update if function names change) ...
from langgraph.graph import StateGraph, END
from .state import GraphState
from pathlib import Path


# --- Import prompt functions (Assuming they will be renamed too) ---
from .prompts import (
    fetch_zero_shot_prompt,  
    fetch_few_shot_prompt,  
    assemble_structured_prompt,
    generate_table_prediction_prompt
)
# -------------------------------------------------

# --- Import schema utility functions ---
from .schema_utils import (
    get_all_table_names_and_descriptions, # Renamed function
    call_prediction_llm,
    fetch_specific_metadata
)
# -------------------------------------------------
from .sql_gen import call_llm_node # Node handling LLM calls (class-based)
import logging

# --- Logger Setup ---
logger = logging.getLogger(__name__)

# --- Node Functions (route_preparation, decide_prompt_strategy remain the same) ---
def route_preparation(state: GraphState) -> GraphState:
    """Node executed before routing. Can be used for pre-processing."""
    logger.debug("Entering route_preparation node.")
    return state

def start_structured_path(state: GraphState) -> GraphState:
    """Logical entry point node for the structured path."""
    logger.debug("Entering start_structured_path node.")
    return state

def decide_prompt_strategy(state: GraphState) -> str:
    strategy = state.get('prompt_strategy', 'Zero-Shot')
    logger.info(f"Routing based on strategy: {strategy}")
    # Map strategy to the NEW node names used in add_conditional_edges map
    if strategy == "Zero-Shot": return "run_zero_shot"
    if strategy == "Few-Shot": return "run_few_shot"
    if strategy == "Structured/Domain-Specific": return "run_structured_start"
    return "run_zero_shot" # Default

# --- Graph Definition ---
def build_graph():
    workflow = StateGraph(GraphState)
    logger.info("Building LangGraph workflow with correct node locations...")

    # --- Add nodes (Functions imported from correct locations) ---
    workflow.add_node("prepare_routing", route_preparation)
    # Prompt nodes (from prompts.py)
    workflow.add_node("fetch_zero_shot_prompt", fetch_zero_shot_prompt)
    workflow.add_node("fetch_few_shot_prompt", fetch_few_shot_prompt)
    workflow.add_node("generate_table_prediction_prompt", generate_table_prediction_prompt) # <<< Node from prompts.py
    workflow.add_node("assemble_structured_prompt", assemble_structured_prompt)
    # Structured path helper nodes (from schema_utils.py)
    workflow.add_node("execute_structured_workflow", start_structured_path)
    workflow.add_node("get_all_table_names_and_descriptions", get_all_table_names_and_descriptions)
    workflow.add_node("call_prediction_llm", call_prediction_llm) # <<< Node from schema_utils.py
    workflow.add_node("fetch_specific_metadata", fetch_specific_metadata)
    # Final SQL generation node (from sql_gen.py)
    workflow.add_node("generate_sql", call_llm_node)
    logger.info("Nodes added from prompts.py, schema_utils.py, and sql_gen.py")

    # --- Define edges ---
    workflow.set_entry_point("prepare_routing")

    # Conditional edges from the start
    workflow.add_conditional_edges(
        "prepare_routing",
        decide_prompt_strategy,
        {
            "run_zero_shot": "fetch_zero_shot_prompt",
            "run_few_shot": "fetch_few_shot_prompt",
            "run_structured_start": "execute_structured_workflow" # Start structured path
        }
    )
    logger.info("Added conditional edges for prompt strategies.")

    # Edge from structured path start node
    workflow.add_edge("execute_structured_workflow", "get_all_table_names_and_descriptions")

    # --- >>> Edges for the Corrected Structured Path sequence <<< ---
    workflow.add_edge("get_all_table_names_and_descriptions", "generate_table_prediction_prompt") # Get tables -> Generate prediction prompt (in prompts.py)
    workflow.add_edge("generate_table_prediction_prompt", "call_prediction_llm") # Prediction prompt -> Call prediction LLM (in schema_utils.py)
    workflow.add_edge("call_prediction_llm", "fetch_specific_metadata") # Prediction result -> Fetch metadata (in schema_utils.py)
    workflow.add_edge("fetch_specific_metadata", "assemble_structured_prompt") # Metadata -> Assemble final prompt (in prompts.py)
    # --- >>> End Structured Path Edges <<< ---

    # Edges converging to the final SQL generation node
    workflow.add_edge("fetch_zero_shot_prompt", "generate_sql")
    workflow.add_edge("fetch_few_shot_prompt", "generate_sql")
    workflow.add_edge("assemble_structured_prompt", "generate_sql") # Assembled prompt goes to SQL gen
    logger.info("Added edges from all prompt paths to generate_sql.")

    # Final edge
    workflow.add_edge("generate_sql", END)
    logger.info("Added edge: generate_sql -> END.")

    # Compile the graph
    app = workflow.compile()
    logger.info("LangGraph graph compiled successfully.")
    return app

# --- Compile graph when module is loaded ---
# This assumes build_graph() is safe to call at import time.
# If build_graph depends on runtime configs, move compilation inside run_nl2sql_graph
compiled_graph = build_graph()

# --- Entry point function for external calls (e.g., Streamlit) ---
def run_nl2sql_graph(nl_query: str, prompt_strategy: str, selected_llm: str, dataset_name: str) -> dict:
    logger.info(f"Invoking NL2SQL graph: Query='{nl_query}', Strategy='{prompt_strategy}', LLM='{selected_llm}', Dataset='{dataset_name}'")
    initial_state = GraphState(
        nl_query=nl_query, prompt_strategy=prompt_strategy, llm_config=selected_llm, dataset_name=dataset_name,
        # Reset all intermediate states
        all_tables_names_descs=None,
        prediction_prompt=None, # <<< Initialize new state key
        relevant_table_names=None,
        relevant_schema_metadata=None,
        final_prompt=None,
        generated_sql=None,
        error=None
    )
    try:
        final_state = compiled_graph.invoke(initial_state)
        logger.info("Graph execution finished.")
        return final_state
    except Exception as e:
        logger.error(f"Graph invocation failed: {e}", exc_info=True)
        error_message = f"Graph Invocation Error: {e}"
        if isinstance(e, KeyError): error_message = f"Graph Invocation Error: Routing key {e} not found."
        return {**initial_state, "error": error_message}

# --- Visualization logic when run directly as a module ---
if __name__ == "__main__":
    # Basic logging setup for standalone execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Running graph module directly for visualization...")

    # --- Option 1: Save visualization to a file ---
    output_filename = "graph_visualization_mermaid.png"
    # Save relative to the current working directory when run with -m
    output_path = Path.cwd() / "graph_logic" / output_filename
    try:
        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Attempting to generate graph visualization PNG and save to {output_path}")

        # Generate PNG bytes using Mermaid rendering
        png_bytes = compiled_graph.get_graph().draw_mermaid_png()

        if not png_bytes:
             raise ValueError("draw_mermaid_png() returned empty data.")

        # Save the PNG bytes to a file
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        logger.info(f"Graph visualization PNG saved successfully to: {output_path}")
        print(f"\nGraph visualization saved to: {output_path}")

    except ImportError as e:
        logger.error(f"Visualization failed: Dependency missing - {e}")
        logger.error("Ensure all LangGraph dependencies, including any needed for Mermaid rendering (like playwright), are installed.")
        print(f"\nERROR: Failed to save visualization PNG due to potentially missing dependencies: {e}")
        print("Try: pip install playwright && playwright install --with-deps")
    except AttributeError as e:
         if "get_graph" in str(e) or "draw_mermaid_png" in str(e):
              logger.error(f"Visualization failed: Method not found. Check langgraph version. Error: {e}")
              print("\nERROR: Failed to save visualization PNG. Method like `.get_graph().draw_mermaid_png()` might not be available.")
         else:
              logger.error(f"Visualization failed with unexpected AttributeError: {e}", exc_info=True)
              print(f"\nERROR: An unexpected attribute error occurred during PNG saving: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during visualization PNG saving: {e}", exc_info=True)
        print(f"\nERROR: Failed to save visualization PNG: {e}")
