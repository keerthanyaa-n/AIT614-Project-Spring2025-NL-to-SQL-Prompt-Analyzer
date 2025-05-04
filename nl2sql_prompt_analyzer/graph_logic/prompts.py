# graph_logic/prompts.py
from .state import GraphState
import logging

from typing import Optional, Dict
from .sql_gen import get_llm_client

logger = logging.getLogger(__name__)

# Node for Zero-Shot Prompt
def fetch_zero_shot_prompt(state: GraphState) -> GraphState:
    """Generates the prompt for the Zero-Shot strategy."""
    logger.debug("Entering generate_zero_shot_prompt node.")
    nl_query = state['nl_query']
    prompt = f"Translate the following question to SQL: {nl_query}. ONLY output the SQL query. Do not include explanations, markdown formatting (like ```sql), or any other text."
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
    prompt = f"{examples}\n# Translate the following question to SQL: {nl_query}. ONLY output the SQL query. Do not include explanations, markdown formatting (like ```sql), or any other text."
    logger.info("Generated Few-Shot prompt (with placeholder examples).")
    return {"final_prompt": prompt}

# --- Node: Generate Prompt for Table Prediction ---
def generate_table_prediction_prompt(state: GraphState) -> Dict[str, Optional[str]]:
    """
    Generates ONLY the prompt string for the LLM that predicts relevant tables.
    Does NOT call the LLM.
    """
    logger.debug("Entering generate_table_prediction_prompt node.")
    nl_query = state.get("nl_query")
    all_tables_info = state.get("all_tables_names_descs") # Expects list of {"name": ..., "description": ...}

    # Input validation
    if not nl_query: logger.error("NL Query missing."); return {"prediction_prompt": None, "error": "NL Query missing for prediction"}
    if all_tables_info is None: logger.error("Table list/descriptions missing."); return {"prediction_prompt": None, "error": "Table list/descriptions missing for prediction"}
    if not all_tables_info: logger.warning("Table list is empty."); return {"prediction_prompt": f"User Question: \"{nl_query}\"\n\nAvailable Tables: None.\n\nRelevant Table Names:", "error": None}

    # Format table names and descriptions
    table_context_lines = [f"- {tbl.get('name', 'Unknown')}: {tbl.get('description', 'N/A')}" for tbl in all_tables_info]
    table_context_string = "\n".join(table_context_lines)

    # Define the prompt structure
    prediction_prompt = f"""Given the user's question and the available database tables with their descriptions, identify the tables most likely needed to answer the question.

User Question: "{nl_query}"

Available Tables:
{table_context_string}

List only the names of the relevant tables, separated by commas. If no tables seem relevant, output 'None'.
Relevant Table Names:"""

    logger.info("Generated prompt string for table prediction.")
    logger.debug(f"Table Prediction Prompt String:\n{prediction_prompt}")

    # Return ONLY the prompt string to the state
    return {"prediction_prompt": prediction_prompt}


# --- Node: Assemble Final Structured Prompt ---
def assemble_structured_prompt(state: GraphState) -> Dict[str, Optional[str]]:
    """
    Assembles the final prompt string using the specific schema details fetched statically.
    Does NOT call the LLM.
    """
    logger.debug("Entering assemble_structured_prompt node.")
    nl_query = state.get('nl_query')
    metadata_dict = state.get('relevant_schema_metadata') # Expects dict {table_name: schema_dict}

    if not nl_query: logger.error("NL Query missing."); return {"final_prompt": None, "error": "NL Query missing"}
    if metadata_dict is None: logger.error("Metadata missing."); return {"final_prompt": None, "error": "Metadata fetching failed."}

    if not metadata_dict:
        schema_string = "[No schema information available for relevant tables]"
        logger.warning("Assembling prompt without specific metadata.")
    else:
        schema_parts = []
        for table_name, table_info in metadata_dict.items():
            parts = [f"Table: {table_name}"]
            if table_info.get("description"): parts.append(f"Description: {table_info['description']}")
            if table_info.get("columns"): parts.append(f"Columns:\n  " + table_info['columns'].replace('\n', '\n  '))
            if table_info.get("foreign_keys"):
                fk_lines = ["Foreign Keys:"]
                for fk in table_info["foreign_keys"]: fk_lines.append(f"  FOREIGN KEY ({fk['column']}) REFERENCES {fk['references_table']}({fk['references_column']})")
                parts.append("\n".join(fk_lines))
            schema_parts.append("\n".join(parts))
        schema_string = "\n\n".join(schema_parts)

    prompt = f"""Given the following database schema for relevant tables (PostgreSQL syntax):

{schema_string}

Translate the following question to SQL: {nl_query}"""
    logger.info("Assembled final structured prompt string using detailed static format.")
    logger.debug(f"Final prompt string content (before LLM client instructions):\n{prompt}")
    return {"final_prompt": prompt}

