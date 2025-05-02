# graph_logic/prompts.py
from .state import GraphState
import logging

logger = logging.getLogger(__name__)

# Node for Zero-Shot Prompt
def fetch_zero_shot_prompt(state: GraphState) -> GraphState:
    """Generates the prompt for the Zero-Shot strategy."""
    logger.debug("Entering generate_zero_shot_prompt node.")
    nl_query = state['nl_query']
    prompt = f"Translate the following question to SQL: {nl_query}"
    logger.info("Generated Zero-Shot prompt.")
    return {"final_prompt": prompt}

# Node for Few-Shot Prompt
def fetch_few_shot_prompt(state: GraphState) -> GraphState:
    """
    Generates the prompt for the Few-Shot strategy.
    (Placeholder: Real implementation would fetch/format examples)
    """
    logger.debug("Entering generate_few_shot_prompt node.")
    nl_query = state['nl_query']
    # Placeholder examples - ideally fetched based on dataset context or config
    examples = (
        "# Example Q: List all customer names\nSELECT name FROM customers;\n"
        "# Example Q: Count orders for user 5\nSELECT COUNT(*) FROM orders WHERE user_id = 5;\n"
    )
    prompt = f"{examples}\n# Translate the following question to SQL: {nl_query}"
    logger.info("Generated Few-Shot prompt (with placeholder examples).")
    return {"final_prompt": prompt}

# Node for Structured/Domain-Specific Prompt
def fetch_structured_prompt(state: GraphState) -> GraphState:
    """
    Generates the prompt for the Structured/Domain-Specific strategy.
    (Placeholder: Real implementation would fetch/format schema)
    """
    logger.debug("Entering generate_structured_prompt node.")
    nl_query = state['nl_query']
    # Placeholder schema - ideally fetched based on dataset context or config
    # Could be fetched in a previous node and accessed via state['dataset_context']
    schema_info = state.get("dataset_context", {}).get("schema", "[Schema information not available]")
    prompt = f"Given the database schema:\n{schema_info}\n\nTranslate the following question to SQL: {nl_query}"
    logger.info("Generated Structured/Domain-Specific prompt (with placeholder schema).")
    return {"final_prompt": prompt}

# (Optional) Node to fetch schema if needed for structured prompts
def fetch_schema_for_structured(state: GraphState) -> GraphState:
     """
     Placeholder node specifically for fetching schema info needed
     ONLY for the structured prompt path.
     """
     logger.debug("Entering fetch_schema_for_structured node.")
     # Simulate fetching schema based on dataset name maybe passed in config?
     schema = "Table: products(id INT, name VARCHAR, category VARCHAR)\nTable: sales(sale_id INT, product_id INT, sale_amount DECIMAL)"
     logger.info("Fetched placeholder schema info.")
     # Ensure dataset_context exists before updating
     current_context = state.get("dataset_context", {})
     current_context['schema'] = schema
     return {"dataset_context": current_context}

# graph_logic/prompts.py

def fetch_structured_prompt(state: GraphState) -> GraphState:
    """
    Fetches/Assembles the prompt for the Structured/Domain-Specific strategy.
    (Placeholder: Real implementation would fetch/format schema)
    """
    logger.debug("Entering fetch_structured_prompt node.")
    nl_query = state['nl_query']

    # --- >>> Likely Problem Area <<< ---
    # This line tries to get 'dataset_context', default to {}, then get 'schema'
    # schema_info = state.get("dataset_context", {}).get("schema", "[Schema information not available]")
    # --- >>> End Problem Area <<< ---

    # --- >>> CORRECTED CODE <<< ---
    # Safely get the context dictionary, defaulting to {} if it's None or missing
    context_dict = state.get("dataset_context") or {}
    # Now safely get the schema from the dictionary
    schema_info = context_dict.get("schema", "[Schema information not available]")
    # --- >>> END CORRECTION <<< ---

    prompt = f"Given the database schema:\n{schema_info}\n\nTranslate the following question to SQL: {nl_query}"
    logger.info("Fetched/Assembled Structured/Domain-Specific prompt (with placeholder schema).")
    return {"final_prompt": prompt}