# storage/sql_connector.py
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd # For result formatting

# --- Try importing psycopg ---
try:
    import psycopg
    from psycopg import OperationalError, ProgrammingError
except ImportError:
    print("ERROR: psycopg library not found. Please install it: pip install psycopg")
    psycopg = None
    OperationalError = Exception # Define dummy errors if import fails
    ProgrammingError = Exception
# -----------------------------

# --- Load .env file ---
# Ensure dotenv is loaded (usually done in db_handler or main app)
# For robustness if run standalone, load here too.
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, override=True)
# --------------------

logger = logging.getLogger(__name__)

# --- Get PostgreSQL Connection Details from Environment ---
PG_HOST = os.environ.get("PG_HOST", "localhost") # Default to localhost
PG_PORT = os.environ.get("PG_PORT", "5432")      # Default PG port
PG_USER = os.environ.get("PG_USER")
PG_PASSWORD = os.environ.get("PG_PASSWORD")
PG_DBNAME_BENCHMARK = os.environ.get("PG_DBNAME_BENCHMARK")
PG_DBNAME_REALWORLD = os.environ.get("PG_DBNAME_REALWORLD")
# ------------------------------------------------------

# Dictionary to cache connections (optional)
_connections: Dict[str, Optional[psycopg.Connection]] = {}

def get_sql_connection(dataset_name: str) -> Optional[psycopg.Connection]:
    """
    Establishes and returns a connection to the specified PostgreSQL database.

    Args:
        dataset_name: The name identifying the dataset
                      ("sample-benchmark-manufacturing-cars" or "real-world-manufacturing-cars").

    Returns:
        A psycopg.Connection object or None if connection fails.
    """
    if psycopg is None:
        logger.error("psycopg library is not installed. Cannot connect to PostgreSQL.")
        return None

    # Check if connection already exists in cache (optional)
    # if dataset_name in _connections:
    #     conn = _connections[dataset_name]
    #     if conn and not conn.closed:
    #         try:
    #             # Simple check if connection is usable
    #             conn.cursor().execute("SELECT 1;")
    #             logger.debug(f"Reusing existing PostgreSQL connection for {dataset_name}")
    #             return conn
    #         except (OperationalError, InterfaceError):
    #             logger.warning(f"Cached connection for {dataset_name} is closed or broken. Reconnecting.")
    #             _connections[dataset_name] = None # Remove broken connection
    #     else:
    #          _connections[dataset_name] = None # Remove closed connection

    # Determine the target database name based on the dataset identifier
    target_dbname = None
    if dataset_name == "sample-benchmark-manufacturing-cars":
        target_dbname = PG_DBNAME_BENCHMARK
    elif dataset_name == "real-world-manufacturing-cars":
        target_dbname = PG_DBNAME_REALWORLD
    else:
        logger.error(f"Unknown dataset name provided: {dataset_name}")
        return None

    # Check if required connection details are available
    required_details = [PG_USER, PG_PASSWORD, target_dbname]
    if not all(required_details):
        logger.error(f"Missing required PostgreSQL connection details (User, Password, DBName) for {dataset_name}. Check .env file.")
        return None

    conn_string = f"host='{PG_HOST}' port='{PG_PORT}' dbname='{target_dbname}' user='{PG_USER}' password='{PG_PASSWORD}'"
    # For security, avoid logging the full connection string with password in production
    logger.info(f"Attempting to connect to PostgreSQL: host={PG_HOST}, port={PG_PORT}, dbname={target_dbname}, user={PG_USER}")

    conn = None
    try:
        conn = psycopg.connect(conn_string, connect_timeout=10)
        # Optional: Set autocommit if desired, or manage transactions manually
        # conn.autocommit = True
        logger.info(f"Successfully connected to PostgreSQL database: {target_dbname}")
        # _connections[dataset_name] = conn # Store in cache if reusing
        return conn
    except OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL DB '{target_dbname}': {e}", exc_info=False) # Show less detail for connection errors
        if conn: conn.close() # Ensure cleanup
        # if dataset_name in _connections: del _connections[dataset_name] # Optional cache cleanup
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred connecting to PostgreSQL DB '{target_dbname}': {e}", exc_info=True)
        if conn: conn.close()
        # if dataset_name in _connections: del _connections[dataset_name] # Optional cache cleanup
        return None

def execute_sql_query(sql_query: str, dataset_name: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Executes a given SQL query against the specified dataset's PostgreSQL database.

    Args:
        sql_query: The SQL query string to execute.
        dataset_name: The name of the target dataset.

    Returns:
        A tuple containing:
        - A pandas DataFrame with the results (or None if execution fails or no results).
        - An error message string (or None if execution succeeds).
    """
    conn = get_sql_connection(dataset_name)
    if conn is None:
        err_msg = f"Failed to get PostgreSQL connection for dataset: {dataset_name}"
        logger.error(err_msg)
        return None, err_msg

    logger.info(f"Executing SQL query on PostgreSQL dataset '{dataset_name}':\n{sql_query}")
    results_df: Optional[pd.DataFrame] = None
    error_msg: Optional[str] = None

    try:
        # Use pandas read_sql for simplicity with SELECT statements
        if sql_query.strip().upper().startswith("SELECT"):
            results_df = pd.read_sql_query(sql_query, conn)
            logger.info(f"SELECT query executed successfully. Fetched {len(results_df)} rows.")
        else:
            # For non-SELECT (INSERT, UPDATE, DELETE, CREATE, etc.)
            with conn.cursor() as cur:
                cur.execute(sql_query)
            conn.commit() # Commit changes for modifying queries
            # For non-select, we return an empty DataFrame to indicate success without rows
            # Or include rowcount if desired
            rowcount = cur.rowcount # Get affected row count
            results_df = pd.DataFrame([{"rows_affected": rowcount}]) # Indicate success and rows affected
            logger.info(f"Non-SELECT query executed and committed successfully. Rows affected: {rowcount}")

    except (OperationalError, ProgrammingError) as e:
        error_msg = f"PostgreSQL execution error on dataset '{dataset_name}': {e}"
        logger.error(error_msg, exc_info=True)
        try:
            conn.rollback() # Rollback on error for modifying queries
            logger.info("Transaction rolled back due to error.")
        except Exception as rb_e:
            logger.error(f"Error during rollback: {rb_e}")
    except Exception as e:
        error_msg = f"An unexpected error occurred during SQL execution on '{dataset_name}': {e}"
        logger.error(error_msg, exc_info=True)
    finally:
        # Close connection if not reusing
        # if conn and dataset_name not in _connections:
        if conn: # Close connection after each execution for simplicity now
             try:
                 conn.close()
                 # logger.debug(f"Closed PostgreSQL connection for {dataset_name}")
             except Exception as close_e:
                 logger.error(f"Error closing PostgreSQL connection: {close_e}")

    return results_df, error_msg

# Optional: Function to close connections if reusing them
# def close_all_sql_connections(): ...

