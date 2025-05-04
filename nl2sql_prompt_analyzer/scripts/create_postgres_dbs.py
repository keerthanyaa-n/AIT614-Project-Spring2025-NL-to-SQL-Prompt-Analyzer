# scripts/create_postgres_dbs.py
import logging
import os
from pathlib import Path
from typing import Optional

# --- Try importing psycopg ---
try:
    import psycopg
    from psycopg import OperationalError, sql
    from psycopg.errors import DuplicateDatabase # Import specific error
except ImportError:
    print("ERROR: psycopg library not found. Please install it: pip install psycopg")
    psycopg = None
    OperationalError = Exception
    DuplicateDatabase = Exception # Define dummy error
# -----------------------------

# --- Load .env file ---
from dotenv import load_dotenv
project_root = Path(__file__).resolve().parent.parent # Assumes script is in scripts/
env_path = project_root / 'config' / '.env'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"Loaded environment variables from {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}. Relying on system environment variables.")
# --------------------

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# -------------------------

# --- Get PostgreSQL Connection Details ---
PG_HOST = os.environ.get("PG_HOST", "localhost")
PG_PORT = os.environ.get("PG_PORT", "5432")
PG_USER = os.environ.get("PG_USER")
PG_PASSWORD = os.environ.get("PG_PASSWORD")
PG_DBNAME_BENCHMARK = os.environ.get("PG_DBNAME_BENCHMARK", "car_benchmark") # Default names
PG_DBNAME_REALWORLD = os.environ.get("PG_DBNAME_REALWORLD", "car_realworld") # Default names
# Use a default database (like 'postgres') to connect initially for creating other DBs
PG_DEFAULT_DB = os.environ.get("PG_DEFAULT_DB", "postgres")

# -----------------------------------------

# --- Define Dataset Info ---
datasets_dir = project_root / "datasets"
datasets_to_process = {
    PG_DBNAME_BENCHMARK: datasets_dir / "sample-benchmark-manufacturing-cars.sql",
    PG_DBNAME_REALWORLD: datasets_dir / "real-world-manufacturing-cars.sql"
}
# --------------------------

def get_connection(dbname: Optional[str] = PG_DEFAULT_DB) -> Optional[psycopg.Connection]:
    """Establishes a connection to a specific PostgreSQL database."""
    if not psycopg: return None
    if not all([PG_USER, PG_PASSWORD, dbname]):
        logger.error(f"Missing connection details (User, Password, DBName='{dbname}')")
        return None

    conn_string = f"host='{PG_HOST}' port='{PG_PORT}' dbname='{dbname}' user='{PG_USER}' password='{PG_PASSWORD}'"
    logger.info(f"Attempting connection to DB: '{dbname}' on {PG_HOST}:{PG_PORT} as user '{PG_USER}'")
    (f"DEBUG: PG_PASSWORD read from environment: '{PG_PASSWORD}'")
    try:
        conn = psycopg.connect(conn_string, connect_timeout=10)
        logger.info(f"Connected successfully to DB: '{dbname}'")
        return conn
    except OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL DB '{dbname}': {e}", exc_info=False)
        return None
    except Exception as e:
        logger.error(f"Unexpected error connecting to PostgreSQL DB '{dbname}': {e}", exc_info=True)
        return None

def create_databases():
    """Connects to the default DB and creates the target databases if they don't exist."""
    logger.info("--- Starting Database Creation Phase ---")
    conn = get_connection(dbname=PG_DEFAULT_DB) # Connect to default DB
    if conn is None:
        logger.error("Cannot proceed: Failed to connect to default PostgreSQL database.")
        return False

    created_any = False
    # Set autocommit to true for CREATE DATABASE command outside transaction block
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for db_name in datasets_to_process.keys():
                logger.info(f"Checking/Creating database: {db_name}")
                try:
                    # Use sql module for safe identifier composition
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                    logger.info(f"Database '{db_name}' created successfully.")
                    created_any = True
                except DuplicateDatabase:
                    logger.warning(f"Database '{db_name}' already exists. Skipping creation.")
                except Exception as e:
                    logger.error(f"Error creating database '{db_name}': {e}", exc_info=True)
                    # If one fails, maybe stop? Or continue? Continuing for now.
    finally:
        conn.autocommit = False # Reset autocommit
        conn.close()
        logger.info("Closed connection to default database.")
    logger.info("--- Finished Database Creation Phase ---")
    return True # Indicate that the phase completed (even if DBs existed)

def populate_database(db_name: str, sql_file_path: Path):
    """Connects to a specific database and executes the SQL script."""
    logger.info(f"--- Populating Database: {db_name} ---")
    if not sql_file_path.is_file():
        logger.error(f"SQL script not found: {sql_file_path}. Skipping population for {db_name}.")
        return

    conn = get_connection(dbname=db_name) # Connect to the specific target DB
    if conn is None:
        logger.error(f"Cannot populate: Failed to connect to target database '{db_name}'.")
        return

    try:
        logger.info(f"Reading SQL script: {sql_file_path}")
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        with conn.cursor() as cur:
            logger.info(f"Executing script in database '{db_name}'...")
            cur.execute(sql_script) # Execute the whole script

        conn.commit() # Commit the transaction
        logger.info(f"Successfully executed script and committed changes in '{db_name}'.")

    except (OperationalError, psycopg.Error) as e:
        logger.error(f"Error executing script in database '{db_name}': {e}", exc_info=True)
        try:
            conn.rollback() # Rollback on error
            logger.info("Transaction rolled back.")
        except Exception as rb_e:
            logger.error(f"Error during rollback: {rb_e}")
    except IOError as e:
        logger.error(f"Error reading SQL file '{sql_file_path}': {e}", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpected error occurred populating '{db_name}': {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logger.info(f"Closed connection to database '{db_name}'.")
    logger.info(f"--- Finished Populating Database: {db_name} ---")


# --- Main execution block ---
if __name__ == "__main__":
    if psycopg is None:
        logger.error("psycopg library not available. Exiting.")
    else:
        logger.info("Starting PostgreSQL database setup process...")
        # 1. Create the databases themselves
        if create_databases():
            # 2. Populate each database with its schema/data script
            for db_name, script_path in datasets_to_process.items():
                populate_database(db_name, script_path)
        logger.info("PostgreSQL database setup process finished.")
