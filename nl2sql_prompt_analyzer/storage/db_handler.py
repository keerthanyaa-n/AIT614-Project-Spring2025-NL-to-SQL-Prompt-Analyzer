# storage/db_handler.py
import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from bson import ObjectId
from pathlib import Path
from dotenv import load_dotenv
import certifi

# --- Logger Setup ---
if not logging.getLogger().hasHandlers():
     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# --------------------

# --- Configuration ---
# --- Load .env file ---
env_path = Path(__file__).parent.parent / 'config' / '.env'
if env_path.is_file():
    logger.info(f"Loading environment variables from: {env_path}")
    load_dotenv(dotenv_path=env_path, override=True)
else:
    logger.warning(f".env file not found at {env_path}. Relying on system environment variables.")
# ---------------------

MONGODB_URI = os.environ.get("MONGODB_CONNECTION_URL")
DATABASE_NAME = "nl2sql_analyzer"
RUNS_COLLECTION = os.environ.get("COLLECTION_NAME")
FEEDBACK_COLLECTION = "run_feedback"

# --- Global Client Variable ---
_mongo_client: Optional[MongoClient] = None

# --- Connection Function ---
def get_mongo_client() -> Optional[MongoClient]:
    """
    Establishes and returns a MongoDB client connection.
    Uses certifi for TLS CA verification.
    """
    global _mongo_client
    if _mongo_client:
        try:
            _mongo_client.admin.command('ping')
            return _mongo_client
        except ConnectionFailure:
            logger.warning("Existing MongoDB client connection failed ping test. Reconnecting.")
            _mongo_client = None

    if not MONGODB_URI:
        logger.error("MONGODB_CONNECTION_URL not found in environment variables or .env file. Cannot connect to database.")
        return None

    try:
        ca_path = certifi.where()
        logger.info(f"Using certifi CA bundle path: {ca_path}")
        logger.info(f"Attempting to connect to MongoDB (URI loaded, starts with: {MONGODB_URI[:20]}...)")
        client = MongoClient(
            MONGODB_URI,
            tls=True,
            tlsCAFile=ca_path,
            serverSelectionTimeoutMS=5000
        )
        client.admin.command('ping')
        logger.info("MongoDB connection successful.")
        _mongo_client = client
        return _mongo_client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}", exc_info=True)
        _mongo_client = None
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during MongoDB connection: {e}", exc_info=True)
        _mongo_client = None
        return None

# --- get_database remains the same ---
def get_database():
    client = get_mongo_client()
    if client: # Client object *can* be checked implicitly or use 'is not None'
        try: return client[DATABASE_NAME]
        except Exception as e: logger.error(f"Failed to get database '{DATABASE_NAME}': {e}", exc_info=True); return None
    return None

# --- Corrected Checks in Collection Getters ---
def get_runs_collection():
    """Gets the collection for storing experiment runs."""
    db = get_database()
    # --- Use explicit None check for database object ---
    if db is not None:
        try:
            print("[DEBUG] - collection", db[RUNS_COLLECTION])
            return db[RUNS_COLLECTION]
        except Exception as e:
            logger.error(f"Failed to get collection '{RUNS_COLLECTION}': {e}", exc_info=True)
            return None
    else: # Handle case where get_database() returned None
        logger.error("Cannot get runs collection: Database connection failed.")
        return None

def get_feedback_collection():
    """Gets the collection for storing feedback (if using separate collection)."""
    db = get_database()
    # --- Use explicit None check for database object ---
    if db is not None:
        try:
            return db[FEEDBACK_COLLECTION]
        except Exception as e:
            logger.error(f"Failed to get collection '{FEEDBACK_COLLECTION}': {e}", exc_info=True)
            return None
    else: # Handle case where get_database() returned None
        logger.error("Cannot get feedback collection: Database connection failed.")
        return None
# --- End Corrected Checks ---

def get_distinct_field_values(field_name: str) -> List[str]:
    """
    Fetches the distinct non-null values for a given field from the runs collection.

    Args:
        field_name: The name of the field to get distinct values for (e.g., "dataset", "llm").

    Returns:
        A list of distinct string values found for that field, or an empty list on error/no data.
    """
    collection = get_runs_collection()
    if collection is None:
        logger.error(f"Cannot get distinct values for '{field_name}': Failed to get runs collection.")
        return []

    try:
        logger.info(f"Fetching distinct values for field: '{field_name}'")
        # Find documents where the field exists and is not null
        distinct_values = collection.distinct(field_name, {field_name: {"$ne": None}})
        # Filter out any potential non-string values if needed, although dataset/llm/prompt should be strings
        string_values = [str(val) for val in distinct_values if isinstance(val, str)]
        logger.info(f"Found {len(string_values)} distinct values for '{field_name}': {string_values}")
        return string_values
    except OperationFailure as e:
        logger.error(f"Failed to get distinct values for '{field_name}' (OperationFailure): {e.details}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching distinct values for '{field_name}': {e}", exc_info=True)
        return []


# --- Updated Checks in Logging/Fetching Functions ---
def log_result(run_context: Dict[str, Any]) -> Optional[str]:
    """Logs the details of a completed NL2SQL run to the database."""
    collection = get_runs_collection()
    # --- Use explicit None check for collection object ---
    if collection is None:
        logger.error("Cannot log result: Failed to get runs collection.")
        return None
    # ---
    log_entry = {"timestamp": datetime.now(timezone.utc), **run_context}
    log_entry.setdefault("em_score", None)
    log_entry.setdefault("exec_acc_score", None)
    log_entry.setdefault("feedback", None)
    try:
        logger.info(f"Log entry (before insertion) : {log_entry}")
        insert_result = collection.insert_one(log_entry)
        inserted_id = insert_result.inserted_id
        logger.info(f"Inserted data : {insert_result}")
        logger.info(f"Successfully logged run result with ID: {inserted_id}")
        return str(inserted_id)
    except OperationFailure as e: logger.error(f"Failed to log run result (OperationFailure): {e.details}", exc_info=True); return None
    except Exception as e: logger.error(f"An unexpected error occurred during result logging: {e}", exc_info=True); return None

def save_feedback(run_id: str, rating: str, issues: List[str], comment: str) -> bool:
    """Saves user feedback, associating it with a specific run record."""
    collection = get_runs_collection()
    # --- Use explicit None check for collection object ---
    if collection is None:
        logger.error("Cannot save feedback: Failed to get runs collection.")
        return False
    # ---
    try: object_id = ObjectId(run_id)
    except Exception: logger.error(f"Invalid run_id format: '{run_id}'."); return False
    feedback_data = {"rating": rating, "issues": issues, "comment": comment, "timestamp": datetime.now(timezone.utc)}
    try:
        update_result = collection.update_one({"_id": object_id}, {"$set": {"feedback": feedback_data}})
        if update_result.matched_count == 0: logger.error(f"Feedback save failed: No run found with ID: {run_id}"); return False
        if update_result.modified_count == 0 and update_result.matched_count == 1: logger.warning(f"Feedback for run ID {run_id} submitted, but no modification (identical?)."); return True
        logger.info(f"Successfully saved feedback for run ID: {run_id}")
        return True
    except OperationFailure as e: logger.error(f"Failed to save feedback (OperationFailure) for run ID {run_id}: {e.details}", exc_info=True); return False
    except Exception as e: logger.error(f"An unexpected error occurred during feedback saving for run ID {run_id}: {e}", exc_info=True); return False

def fetch_run_history(run_id: Optional[str] = None, dataset: Optional[str] = None, prompt_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """ Fetches run history from the database based on optional filters. """
    collection = get_runs_collection()
    # --- Use explicit None check for collection object ---
    if collection is None:
        logger.error("Cannot fetch history: Failed to get runs collection.")
        return []
    # ---
    query_filter = {}
    if run_id:
        try: query_filter["_id"] = ObjectId(run_id)
        except Exception: logger.warning(f"Invalid run_id format: '{run_id}'. Ignoring filter.")
    if dataset: query_filter["dataset"] = dataset
    if prompt_type: query_filter["prompt_type"] = prompt_type
    try:
        logger.info(f"Fetching run history with filter: {query_filter}, limit: {limit}")
        cursor = collection.find(query_filter).sort("timestamp", -1).limit(limit)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        logger.info(f"Found {len(results)} history records.")
        return results
    except OperationFailure as e: logger.error(f"Failed to fetch run history (OperationFailure): {e.details}", exc_info=True); return []
    except Exception as e: logger.error(f"An unexpected error occurred during history fetching: {e}", exc_info=True); return []
# --- End Updated Checks ---

#############################################
# Analytics tab functions
#############################################
def get_overall_stats() -> Optional[Dict[str, Any]]:
    """
    Calculates overall average statistics (duration, tokens) and error rates
    across all completed runs in the database.

    Returns:
        A dictionary containing overall stats, or None if an error occurs.
        Example: {
            'total_runs': 150,
            'avg_duration_sec': 3.5,
            'avg_total_gen_tokens': 450.2,
            'avg_total_pred_tokens': 55.1, # Only includes runs where prediction happened
            'llm_graph_error_rate': 0.05, # 5%
            'sql_exec_success_rate': 0.85 # 85%
        }
    """
    collection = get_runs_collection()
    if collection is None:
        logger.error("Cannot get overall stats: Failed to get runs collection.")
        return None

    # Define the aggregation pipeline
    pipeline = [
        {
            # Stage 1: Group all documents together and calculate sums and counts
            '$group': {
                '_id': None, # Group all documents into one
                'total_runs': {'$sum': 1},
                'total_duration': {'$sum': '$duration_sec'},
                # Sum tokens only if they exist (handle potential nulls)
                'total_gen_tokens': {'$sum': {'$ifNull': ['$generation_total_tokens', 0]}},
                'total_pred_tokens': {'$sum': {'$ifNull': ['$prediction_total_tokens', 0]}},
                # Count runs where prediction tokens were logged (structured path)
                'count_pred_runs': {'$sum': {'$cond': [{'$ne': ['$prediction_total_tokens', None]}, 1, 0]}},
                # Count errors (LLM/Graph or SQL Execution)
                'llm_graph_error_count': {
                    '$sum': {
                        '$cond': [
                            {'$or': [
                                {'$ne': ['$graph_error', None]},
                                {'$and': [ # Check if generated_sql exists and starts with error/warning
                                    {'$ne': ['$generated_sql', None]},
                                    {'$or': [
                                        {'$regexMatch': {'input': '$generated_sql', 'regex': '^-- ERROR:'}},
                                        {'$regexMatch': {'input': '$generated_sql', 'regex': '^-- WARNING:'}}
                                    ]}
                                ]}
                            ]},
                            1, 0
                        ]
                    }
                },
                'sql_exec_success_count': {
                     # Count successes where sql_exec_error is null or empty string
                    '$sum': {
                        '$cond': [{'$in': ['$sql_exec_error', [None, ""]]}, 1, 0]
                    }
                }
            }
        },
        {
            # Stage 2: Project the final calculated averages and rates
            '$project': {
                '_id': 0, # Exclude the default _id field
                'total_runs': 1,
                'avg_duration_sec': {'$divide': ['$total_duration', '$total_runs']},
                'avg_total_gen_tokens': {'$divide': ['$total_gen_tokens', '$total_runs']},
                # Calculate avg prediction tokens only based on runs that had prediction
                'avg_total_pred_tokens': {
                    '$cond': [
                        {'$gt': ['$count_pred_runs', 0]},
                        {'$divide': ['$total_pred_tokens', '$count_pred_runs']},
                        None # Return null if no runs had prediction tokens
                    ]
                },
                'llm_graph_error_rate': {'$divide': ['$llm_graph_error_count', '$total_runs']},
                'sql_exec_success_rate': {'$divide': ['$sql_exec_success_count', '$total_runs']}
            }
        }
    ]

    try:
        logger.info("Executing overall stats aggregation pipeline...")
        result = list(collection.aggregate(pipeline))
        if result:
            stats = result[0]
            logger.info(f"Overall stats calculated: {stats}")
            return stats
        else:
            logger.warning("Overall stats aggregation returned no results (collection might be empty).")
            return {} # Return empty dict if no documents found
    except OperationFailure as e:
        logger.error(f"Failed to get overall stats (OperationFailure): {e.details}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during overall stats aggregation: {e}", exc_info=True)
        return None


def get_stats_by_group(group_by_fields: List[str], filters: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Calculates average statistics (duration, tokens) and error rates, grouped by
    specified fields and optionally filtered.

    Args:
        group_by_fields: A list of field names to group by (e.g., ["dataset", "prompt_type"]).
                         Valid fields: "dataset", "prompt_type", "llm".
        filters: An optional dictionary for filtering data before aggregation
                 (e.g., {"dataset": "real-world-manufacturing-cars"}).

    Returns:
        A list of dictionaries, each containing the group keys and calculated stats,
        or None if an error occurs. Returns empty list if no matching data found.
        Example for group_by_fields=["dataset", "prompt_type"]:
        [
            {
                "_id": {"dataset": "real-world...", "prompt_type": "Zero-Shot"},
                "count": 50,
                "avg_duration_sec": 2.8,
                "avg_total_gen_tokens": 400.5,
                "avg_total_pred_tokens": null, # Prediction step didn't run for Zero-Shot
                "llm_graph_error_rate": 0.02,
                "sql_exec_success_rate": 0.90
            },
            {
                "_id": {"dataset": "real-world...", "prompt_type": "Structured/Domain-Specific"},
                "count": 55,
                "avg_duration_sec": 4.5,
                "avg_total_gen_tokens": 550.0,
                "avg_total_pred_tokens": 60.1, # Prediction step ran
                "llm_graph_error_rate": 0.04,
                "sql_exec_success_rate": 0.95
            },
            ...
        ]
    """
    collection = get_runs_collection()
    if collection is None:
        logger.error("Cannot get grouped stats: Failed to get runs collection.")
        return None

    if not group_by_fields:
        logger.error("Cannot get grouped stats: group_by_fields list cannot be empty.")
        return None

    # Validate group_by fields
    valid_group_fields = {"dataset", "prompt_type", "llm"}
    if not all(field in valid_group_fields for field in group_by_fields):
         logger.error(f"Invalid field found in group_by_fields. Allowed fields: {valid_group_fields}")
         return None

    pipeline = []

    # Stage 1: Optional $match stage based on filters
    if filters:
        match_stage = {'$match': filters}
        pipeline.append(match_stage)
        logger.info(f"Applying filter to aggregation: {filters}")

    # Stage 2: $group stage
    group_id = {field: f"${field}" for field in group_by_fields} # Create _id structure for grouping
    group_stage = {
        '$group': {
            '_id': group_id,
            'count': {'$sum': 1},
            'total_duration': {'$sum': '$duration_sec'},
            'total_gen_tokens': {'$sum': {'$ifNull': ['$generation_total_tokens', 0]}},
            'total_pred_tokens': {'$sum': {'$ifNull': ['$prediction_total_tokens', 0]}},
            'count_pred_runs': {'$sum': {'$cond': [{'$ne': ['$prediction_total_tokens', None]}, 1, 0]}},
            'llm_graph_error_count': {
                '$sum': {'$cond': [{'$or': [ {'$ne': ['$graph_error', None]}, {'$and': [ {'$ne': ['$generated_sql', None]}, {'$or': [ {'$regexMatch': {'input': '$generated_sql', 'regex': '^-- ERROR:'}}, {'$regexMatch': {'input': '$generated_sql', 'regex': '^-- WARNING:'}} ]} ]} ]}, 1, 0 ]}
            },
            'sql_exec_success_count': {
                '$sum': {'$cond': [{'$in': ['$sql_exec_error', [None, ""]]}, 1, 0]}
            }
        }
    }
    pipeline.append(group_stage)

    # Stage 3: $project stage to calculate averages/rates
    project_stage = {
        '$project': {
            '_id': 1, # Keep the group keys
            'count': 1,
            'avg_duration_sec': {'$divide': ['$total_duration', '$count']},
            'avg_total_gen_tokens': {'$divide': ['$total_gen_tokens', '$count']},
            'avg_total_pred_tokens': {
                '$cond': [ {'$gt': ['$count_pred_runs', 0]}, {'$divide': ['$total_pred_tokens', '$count_pred_runs']}, None ]
            },
            'llm_graph_error_rate': {'$divide': ['$llm_graph_error_count', '$count']},
            'sql_exec_success_rate': {'$divide': ['$sql_exec_success_count', '$count']}
        }
    }
    pipeline.append(project_stage)

    # Stage 4: Optional $sort stage (e.g., sort by dataset then prompt type)
    sort_stage = {'$sort': {'_id': 1}} # Sort by the group keys
    pipeline.append(sort_stage)


    try:
        logger.info(f"Executing grouped stats aggregation pipeline (grouping by: {group_by_fields})...")
        # Log the pipeline structure for debugging if needed (can be verbose)
        # logger.debug(f"Aggregation Pipeline: {json.dumps(pipeline, indent=2)}")
        results = list(collection.aggregate(pipeline))
        logger.info(f"Grouped stats aggregation returned {len(results)} groups.")
        return results # Returns list of dicts like the example
    except OperationFailure as e:
        logger.error(f"Failed to get grouped stats (OperationFailure): {e.details}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during grouped stats aggregation: {e}", exc_info=True)
        return None

def get_feedback_summary_by_prompt() -> Optional[List[Dict[str, Any]]]:
    """
    Calculates the distribution of feedback ratings for each prompt type.

    Returns:
        A list of dictionaries, each containing the prompt type and rating counts,
        or None if an error occurs. Returns empty list if no feedback data found.
        Example:
        [
            {
                "_id": "Zero-Shot",
                "ratings": {"Good": 10, "OK": 5, "Bad": 2},
                "total_feedback": 17
            },
            {
                "_id": "Few-Shot",
                "ratings": {"Very Good": 8, "Good": 12, "OK": 3},
                "total_feedback": 23
            },
            ...
        ]
    """
    collection = get_runs_collection()
    if collection is None:
        logger.error("Cannot get feedback summary: Failed to get runs collection.")
        return None

    # Define the aggregation pipeline
    pipeline = [
        {
            # Stage 1: Filter documents that have feedback submitted
            '$match': {
                'feedback': {'$ne': None},
                'feedback.rating': {'$exists': True, '$ne': None} # Ensure rating exists
            }
        },
        {
            # Stage 2: Group by prompt_type and feedback.rating, count occurrences
            '$group': {
                '_id': {
                    'prompt_type': '$prompt_type',
                    'rating': '$feedback.rating'
                },
                'count': {'$sum': 1}
            }
        },
        {
            # Stage 3: Group again by only prompt_type to consolidate ratings
            '$group': {
                '_id': '$_id.prompt_type', # Group by prompt_type
                'ratings': {
                    '$push': { # Create an array of {rating: count} pairs
                        'k': '$_id.rating',
                        'v': '$count'
                    }
                },
                'total_feedback': {'$sum': '$count'} # Sum counts for total feedback per type
            }
        },
        {
             # Stage 4: Convert the array of key-value pairs into a dictionary
             '$project': {
                 '_id': 1, # Keep prompt_type as _id
                 'ratings': {'$arrayToObject': '$ratings'}, # Convert [{k: r, v: c}, ...] to {r: c, ...}
                 'total_feedback': 1
             }
        },
        {
             # Stage 5: Sort by prompt type name
             '$sort': {
                 '_id': 1
             }
        }
    ]

    try:
        logger.info("Executing feedback summary aggregation pipeline...")
        results = list(collection.aggregate(pipeline))
        logger.info(f"Feedback summary aggregation returned {len(results)} prompt types.")
        return results # Returns list of dicts like the example
    except OperationFailure as e:
        logger.error(f"Failed to get feedback summary (OperationFailure): {e.details}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during feedback summary aggregation: {e}", exc_info=True)
        return None