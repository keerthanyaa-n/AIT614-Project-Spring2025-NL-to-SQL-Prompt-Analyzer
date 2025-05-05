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
    prompt = (
    "Write a valid SQL query that answers the following question as accurately as possible.\n"
    f"{nl_query}\n"
    "Output only the SQL statement, without any explanation, markdown, or formatting."
)
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
    "# Example Q: What are the names of all customers who had a vehicle serviced in April 2025?\n"
    "# SQL: SELECT DISTINCT cr.FstNm, cr.LstNm FROM Client_Registry cr JOIN Svc_Log sl ON cr.ClntId = sl.ClntRef WHERE sl.SvcDt BETWEEN '2025-04-01' AND '2025-04-30';\n\n"
    
    "# Example Q: How many vehicles do we have at each site location?\n"
    "# SQL: SELECT CurrLocId, COUNT(*) AS VehicleCount FROM Vehicle_Inventory GROUP BY CurrLocId;\n\n"
    
    "# Example Q: Which parts supplied by 'SteelWorks Inc.' are used in the Aurora model?\n"
    "# SQL: SELECT DISTINCT pi.PrtNm FROM Part_Inventory pi JOIN Prod_BOM pb ON pi.PrtSKU = pb.PrtId JOIN Prod_Catalog pc ON pb.PrdId = pc.PrdId JOIN Part_Suppliers ps ON pi.PrtSKU = ps.PrtId JOIN Vendor_Master vm ON ps.VndrId = vm.VndrId WHERE pc.MdlNm = 'Aurora' AND vm.VName = 'SteelWorks Inc.';\n\n"
    
    "# Example Q: Which employee has performed the most services overall?\n"
    "# SQL: SELECT pr.FName, pr.LName, COUNT(*) AS TotalServices FROM Svc_Log sl JOIN Personnel_Roster pr ON sl.TechRef = pr.EmpRef GROUP BY pr.FName, pr.LName ORDER BY TotalServices DESC LIMIT 1;\n\n"
    
    "# Example Q: List all standard features for the Zephyr model.\n"
    "# SQL: SELECT pf.FeatName FROM Prod_Catalog pc JOIN Prod_Feature_Avail pfa ON pc.PrdId = pfa.PrdId JOIN Prod_Features pf ON pfa.FeatCd = pf.FeatCd WHERE pc.MdlNm = 'Zephyr' AND pfa.IsStdFlg = TRUE;\n\n"
    
    "# Example Q: What are the names and emails of employees who work at the West Coast Service Hub?\n"
    "# SQL: SELECT FName, LName, CorpEmail FROM Personnel_Roster WHERE WorkLocId = 'SVCW';\n\n"
    
    "# Example Q: Which models have more than 3 parts listed in the bill of materials?\n"
    "# SQL: SELECT pc.MdlNm FROM Prod_Catalog pc JOIN Prod_BOM pb ON pc.PrdId = pb.PrdId GROUP BY pc.MdlNm HAVING COUNT(pb.PrtId) > 3;\n\n"
    
    "# Example Q: What’s the total cost of parts used in service ticket ID 4?\n"
    "# SQL: SELECT SUM(CostBasis) FROM Svc_PartsUsed WHERE SvcTktId = 4;\n\n"
    
    "# Example Q: List the names of departments that have at least one active employee.\n"
    "# SQL: SELECT DISTINCT d.DptName FROM Org_Departments d JOIN Personnel_Roster p ON d.DptCd = p.DptRef WHERE p.IsActiveFlg = TRUE;\n\n"
    
    "# Example Q: Which vehicles were produced in 2025 and are still in inventory?\n"
    "# SQL: SELECT VehVIN FROM Vehicle_Inventory WHERE EXTRACT(YEAR FROM ProdDate) = 2025 AND VehStat = 'INV';"
)

    prompt = f"{examples}\n# Translate the following question to SQL: {nl_query}. ONLY output the SQL query. Output only the SQL statement, without any explanation, markdown, or formatting."
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

