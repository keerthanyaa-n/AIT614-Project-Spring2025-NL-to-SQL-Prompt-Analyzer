# graph_logic/graph.py
# ... (Imports remain the same, but might need to update if function names change) ...
from langgraph.graph import StateGraph, END
from .state import GraphState
from pathlib import Path


# --- Import prompt functions (Assuming they will be renamed too) ---
from .prompts import (
    fetch_zero_shot_prompt,  # <<< Renamed function import
    fetch_few_shot_prompt,   # <<< Renamed function import
    fetch_structured_prompt, # <<< Renamed function import
    fetch_schema_for_structured # Optional
)
# -------------------------------------------------
from .sql_gen import call_llm_node # Node handling LLM calls (class-based)
import logging

# --- Logger Setup ---
logger = logging.getLogger(__name__)

# --- Node Functions (route_preparation, decide_prompt_strategy remain the same) ---
def route_preparation(state: GraphState) -> GraphState:
    logger.debug("Entering route_preparation node.")
    return state

def decide_prompt_strategy(state: GraphState) -> str:
    strategy = state.get('prompt_strategy', 'Zero-Shot')
    logger.info(f"Routing based on strategy: {strategy}")
    # Map strategy to the NEW node names used in add_conditional_edges map
    if strategy == "Zero-Shot": return "run_zero_shot"
    if strategy == "Few-Shot": return "run_few_shot"
    if strategy == "Structured/Domain-Specific": return "run_structured"
    return "run_zero_shot" # Default

# --- Graph Definition ---
def build_graph():
    workflow = StateGraph(GraphState)
    logger.info("Building LangGraph workflow with conditional prompt nodes...")

    # --- Add nodes with NEW names ---
    workflow.add_node("prepare_routing", route_preparation)
    # workflow.add_node("fetch_schema", fetch_schema_for_structured) # Add if using schema fetch node
    workflow.add_node("fetch_zero_shot_prompt", fetch_zero_shot_prompt)   # <<< Renamed node
    workflow.add_node("fetch_few_shot_prompt", fetch_few_shot_prompt)    # <<< Renamed node
    workflow.add_node("fetch_structured_prompt", fetch_structured_prompt) # <<< Renamed node
    workflow.add_node("generate_sql", call_llm_node)
    logger.info("Nodes added: prepare_routing, fetch_zero_shot_prompt, fetch_few_shot_prompt, fetch_structured_prompt, generate_sql")

    # Define entry point
    workflow.set_entry_point("prepare_routing")

    # Conditional edges: Map decision outcome to NEW node names
    workflow.add_conditional_edges(
        "prepare_routing",
        decide_prompt_strategy,
        {
            "run_zero_shot": "fetch_zero_shot_prompt",     
            "run_few_shot": "fetch_few_shot_prompt",      
            "run_structured": "fetch_structured_prompt" 
            # "fetch_schema": "fetch_schema", # Example if using schema node
        }
    )
    logger.info("Added conditional edges for prompt strategies starting from 'prepare_routing'.")

    # --- Add edge if using separate schema fetching ---
    # workflow.add_edge("fetch_schema", "fetch_structured_prompt") # Target node name updated if schema fetching used

    # Edges from renamed prompt nodes to SQL generation
    workflow.add_edge("fetch_zero_shot_prompt", "generate_sql")   
    workflow.add_edge("fetch_few_shot_prompt", "generate_sql")    
    workflow.add_edge("fetch_structured_prompt", "generate_sql") 
    logger.info("Added edges from all prompt nodes to generate_sql.")

    # Final edge
    workflow.add_edge("generate_sql", END)

    # Compile the graph
    app = workflow.compile()
    logger.info("LangGraph graph compiled successfully.")
    return app

# --- Compile graph when module is loaded ---
# This assumes build_graph() is safe to call at import time.
# If build_graph depends on runtime configs, move compilation inside run_nl2sql_graph
compiled_graph = build_graph()

# --- Entry point function for external calls (e.g., Streamlit) ---
def run_nl2sql_graph(nl_query: str, prompt_strategy: str, selected_llm: str) -> dict:
    """
    Invokes the compiled NL2SQL graph with the given inputs.
    Returns the final state dictionary.
    """
    logger.info(f"Invoking NL2SQL graph: Query='{nl_query}', Strategy='{prompt_strategy}', LLM='{selected_llm}'")
    # Initialize the state for the graph run
    initial_state = GraphState(
        nl_query=nl_query,
        prompt_strategy=prompt_strategy,
        llm_config=selected_llm,
        dataset_context=None,
        final_prompt=None,
        generated_sql=None,
        error=None
    )
    try:
        # Execute the graph
        final_state = compiled_graph.invoke(initial_state)
        logger.info("Graph execution finished.")
        # Return the complete final state
        return final_state
    except Exception as e:
        # Log errors during graph execution and return state with error info
        logger.error(f"Graph invocation failed: {e}", exc_info=True)
        return {**initial_state, "error": f"Graph Invocation Error: {e}"}


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
