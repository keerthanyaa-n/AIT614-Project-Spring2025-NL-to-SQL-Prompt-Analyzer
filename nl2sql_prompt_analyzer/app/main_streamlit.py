# app/main_streamlit.py
import streamlit as st
from datetime import date, datetime
import logging
import sys
from pathlib import Path
import pandas as pd
import time # <<< Import the time module

# --- Add project root to path to allow imports ---
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# -------------------------------------------------

from config.logging_config import setup_logging
# --- Placeholder imports for other modules ---
from graph_logic.graphs import run_nl2sql_graph
from storage.db_handler import log_result, save_feedback, fetch_run_history
from storage.sql_connector import execute_sql_query
# -----------------------------------------------


# --- Add project root to path ---
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# ----------------------------------


# --- Initialize Session State ---
# Initialize all keys we will use to persist state across reruns
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False
if 'current_query_context' not in st.session_state:
    st.session_state.current_query_context = {}
if 'results_ready' not in st.session_state: # Flag to know if results area should be shown
    st.session_state.results_ready = False
if 'last_prompt' not in st.session_state:
    st.session_state.last_prompt = None
if 'last_sql' not in st.session_state:
    st.session_state.last_sql = None
if 'last_em_score' not in st.session_state:
    st.session_state.last_em_score = "N/A"
if 'last_exec_acc_score' not in st.session_state:
    st.session_state.last_exec_acc_score = "N/A"
if 'last_duration' not in st.session_state:
    st.session_state.last_duration = 0.0
# Initialize feedback widget states if needed (might help consistency)
if 'feedback_rating_slider' not in st.session_state:
    st.session_state.feedback_rating_slider = "OK"
if 'feedback_issues_multi' not in st.session_state:
    st.session_state.feedback_issues_multi = []
if 'feedback_comment_combo' not in st.session_state:
    st.session_state.feedback_comment_combo = ""
if 'ground_truth_input' not in st.session_state:
    st.session_state.ground_truth_input = ""
# Initialize session history for Session State
if 'history_data' not in st.session_state:
    st.session_state.history_data = None # Store the fetched history (as DataFrame)
if 'history_loaded' not in st.session_state:
    st.session_state.history_loaded = False # Flag to track initial load
if 'sql_exec_result_df' not in st.session_state:
    st.session_state.sql_exec_result_df = None
if 'sql_exec_error' not in st.session_state:
    st.session_state.sql_exec_error = None
# --------------------------------
# --- Setup Logging ---
setup_logging()
logger = logging.getLogger(__name__)
# ---------------------


# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("NL2SQL Prompt Engineering Analyzer")


# logger.info("="*20 + " Streamlit App Started/Refreshed " + "="*20) # Clear marker for app start/rerun

# --- Sidebar for Global Configuration ---
with st.sidebar:
    st.header("Configuration")
    available_datasets = [
        "sample-benchmark-manufacturing-cars",
        "real-world-manufacturing-cars"
    ]
    available_prompt_types = ["Zero-Shot", "Few-Shot", "Structured/Domain-Specific"]
    available_llms = ["GPT-4o Mini", "Gemini 1.5 Flash"]

    selected_dataset = st.selectbox(
        "Select Dataset:",
        options=available_datasets, # Use the new list
        key="sb_dataset" # Keep the key consistent
    )
    selected_prompt_type = st.selectbox("Select Prompt Technique:", available_prompt_types)
    selected_llm = st.selectbox("Select LLM:", available_llms)
    st.divider()

# --- Main Area with Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 NL Query Test", "📈 Evaluation Analytics", "📜 Run History"])

# --- Tab 1: Live NL Query Testing ---
# --- Tab 1: Live NL Query Testing ---
with tab1:
    st.header("Test NL Query to SQL Generation & Execution") # Updated header
    st.write("Enter a query, select parameters, generate SQL, and see execution results.")

    nl_query = st.text_area("Your question:", height=100, key="nl_query_input")

    if st.button("Run Generation & Execution", key="generate_sql_button"):
        # Reset state
        st.session_state.results_ready = False
        st.session_state.show_feedback = False
        st.session_state.last_em_score = "N/A"
        st.session_state.last_exec_acc_score = "N/A"
        st.session_state.last_prompt = None
        st.session_state.last_sql = None
        st.session_state.current_query_context = {}
        # --- >>> Reset execution state <<< ---
        st.session_state.sql_exec_result_df = None
        st.session_state.sql_exec_error = None
        # --- >>> End reset <<< ---


        if not nl_query:
            st.warning("Please enter a natural language query.")
        else:
            logger.info("--- Begin Generate User Query ---")
            logger.info(f"Parameters: Dataset='{selected_dataset}', PromptType='{selected_prompt_type}', LLM='{selected_llm}'")
            logger.info(f"NL Query: '{nl_query}'")
            current_ground_truth = st.session_state.ground_truth_input # Get GT if provided
            if current_ground_truth: logger.info("Ground Truth SQL provided (for later evaluation).")

            start_time = time.perf_counter()

            try:
                # --- 1. Call the backend LangGraph workflow ---
                with st.spinner("Running NL2SQL generation graph..."):
                    logger.info("Invoking backend graph...")
                    graph_result_state = run_nl2sql_graph(
                        nl_query=nl_query, prompt_strategy=selected_prompt_type,
                        selected_llm=selected_llm, dataset_name=selected_dataset
                    )
                    logger.info("Backend graph execution attempt complete.")

                    generated_sql = graph_result_state.get("generated_sql")
                    prompt = graph_result_state.get("final_prompt", "Prompt not captured.")
                    graph_error = graph_result_state.get("error") # Check if graph itself had error

                    # Handle graph errors first
                    if graph_error:
                        raise Exception(f"Graph Error: {graph_error}")
                    if not generated_sql:
                        # Handle case where graph finished but SQL is missing (should have error ideally)
                        raise Exception("Graph execution finished but no SQL was generated.")

                # --- 2. Execute the Generated SQL ---
                st.session_state.sql_exec_result_df = None # Reset before trying
                st.session_state.sql_exec_error = None
                # Only execute if SQL was generated successfully by the LLM
                if generated_sql and not generated_sql.startswith("-- ERROR:") and not generated_sql.startswith("-- WARNING:"):
                    with st.spinner(f"Executing generated SQL on '{selected_dataset}'..."):
                        # Call the function from sql_connector.py
                        exec_df, exec_error = execute_sql_query(generated_sql, selected_dataset)
                        # Store results in session state
                        st.session_state.sql_exec_result_df = exec_df # Stores DataFrame or None
                        st.session_state.sql_exec_error = exec_error # Stores error message or None
                        if exec_error:
                            logger.error(f"SQL Execution Failed for dataset '{selected_dataset}': {exec_error}")
                            # Don't raise exception, just store the error to display it
                        else:
                            logger.info(f"SQL Execution Successful for dataset '{selected_dataset}'.")
                else:
                    # Handle case where LLM returned an error string or empty SQL
                    exec_error_msg = generated_sql if generated_sql else "No SQL generated by LLM."
                    logger.warning(f"Skipping SQL execution: {exec_error_msg}")
                    st.session_state.sql_exec_error = f"Skipped execution: {exec_error_msg}"
                # --- End SQL Execution ---

                # --- 3. Placeholder for Evaluation Logic ---
                # (Evaluation logic remains placeholder for now)
                em_score = "N/A"
                exec_acc_score = "N/A" # This will be updated later based on comparison
                # TODO: Implement comparison logic here if ground_truth_sql exists
                # -----------------------------------------

                end_time = time.perf_counter(); duration = end_time - start_time
                st.success(f"Processing complete in {duration:.3f} seconds!")

                # --- 4. Store results/context in session state ---
                st.session_state.last_prompt = prompt
                st.session_state.last_sql = generated_sql
                st.session_state.last_em_score = em_score
                st.session_state.last_exec_acc_score = exec_acc_score
                st.session_state.last_duration = duration

                # Prepare context dictionary for logging (include execution status)
                run_context_for_log = {
                    "nl_query": nl_query, "dataset": selected_dataset, "prompt_type": selected_prompt_type,
                    "llm": selected_llm, "generated_sql": generated_sql, "prompt": prompt,
                    "ground_truth_sql": current_ground_truth, "em_score": em_score,
                    "exec_acc_score": exec_acc_score, "duration_sec": duration, "graph_error": graph_error,
                    "sql_exec_error": st.session_state.sql_exec_error # Log execution error/status
                }
                # --- Add execution data if successful and convert dates ---
                sql_result_data_for_log = None
                if st.session_state.sql_exec_result_df is not None and st.session_state.sql_exec_error is None:
                    if not st.session_state.sql_exec_result_df.empty:
                         max_log_rows = 50 # Example limit
                         df_to_log = st.session_state.sql_exec_result_df.head(max_log_rows)
                         # Convert DataFrame to list of dictionaries
                         list_of_dicts = df_to_log.to_dict('records')

                         # --- >>> Convert datetime.date to datetime.datetime <<< ---
                         processed_list = []
                         for row_dict in list_of_dicts:
                             processed_row = {}
                             for key, value in row_dict.items():
                                 if isinstance(value, date) and not isinstance(value, datetime):
                                     # Convert date to datetime (setting time to midnight)
                                     processed_row[key] = datetime.combine(value, datetime.min.time())
                                 else:
                                     processed_row[key] = value
                             processed_list.append(processed_row)
                         sql_result_data_for_log = processed_list
                         # --- >>> End Date Conversion <<< ---

                         if len(st.session_state.sql_exec_result_df) > max_log_rows:
                              logger.warning(f"SQL result has {len(st.session_state.sql_exec_result_df)} rows. Logging only first {max_log_rows}.")
                    else:
                         # Log empty list if query returned no rows or was non-SELECT
                         sql_result_data_for_log = []

                run_context_for_log["sql_execution_result_data"] = sql_result_data_for_log # Add results (or None if error/skipped)
                # --- End context preparation ---

                st.session_state.current_query_context = run_context_for_log.copy()

                # --- 5. Log Results to MongoDB ---
                logger.info("Logging results to database...")
                result_id = log_result(run_context_for_log)
                if result_id:
                    st.session_state.current_query_context['mongodb_id'] = result_id
                    st.info(f"Results logged to DB (ID: {result_id}).")
                    logger.info(f"Successfully logged run with MongoDB ID: {result_id}")
                else:
                    st.warning("Failed to log results to database.")
                    logger.error("Failed to get result ID from log_result.")
                # --- End Logging ---

                # Set flags for UI display
                st.session_state.results_ready = True
                st.session_state.show_feedback = True


            except Exception as e:
                # Handle any exceptions during the process
                st.session_state.results_ready = False
                st.session_state.show_feedback = False
                end_time = time.perf_counter()
                duration = end_time - start_time # Duration before error
                logger.error(f"An error occurred in 'Run Generation & Execution': {e}", exc_info=True)
                st.error(f"An error occurred: {e}") # Display error in UI
                st.caption(f"Processing time before error: {duration:.3f} seconds")
            finally:
                 logger.info("--- End Generate User Query Attempt ---")


    # --- Display Results Area ---
    # This section is displayed only if results are ready (flag set in session state)
    if st.session_state.get('results_ready', False):
        st.markdown("---")
        st.subheader("Generated Output")
        # Display the prompt used
        st.text("Generated Prompt:")
        st.code(st.session_state.last_prompt or "N/A", language='text')
        # Display the generated SQL
        st.text("Generated SQL:")
        st.code(st.session_state.last_sql or "N/A", language='sql')
        # Display the ground truth SQL if it was provided
        gt_sql_context = st.session_state.current_query_context.get("ground_truth_sql")
        if gt_sql_context:
             st.text("Ground Truth SQL (For Eval):")
             st.code(gt_sql_context, language='sql')
        # Display evaluation scores (currently placeholders)
        st.markdown(f"**Evaluation Scores (Placeholders):**")
        st.metric("Exact Match (EM) Score", st.session_state.last_em_score)
        st.metric("Execution Accuracy (ExecAcc) Score", st.session_state.last_exec_acc_score)
        st.caption(f"Total processing time: {st.session_state.last_duration:.3f} seconds")

        # --- >>> Display SQL Execution Results <<< ---
        st.markdown("---")
        st.subheader("SQL Execution Result")
        # Check if an error occurred during execution
        if st.session_state.sql_exec_error:
            st.error(f"Execution Failed: {st.session_state.sql_exec_error}")
        # Check if the result DataFrame exists (it might be None if error occurred)
        elif st.session_state.sql_exec_result_df is not None:
            # Check if the DataFrame is empty
            if st.session_state.sql_exec_result_df.empty:
                 # Check if it was an empty result from a non-SELECT query that succeeded
                 if "rows_affected" in st.session_state.sql_exec_result_df.columns:
                     st.success(f"Query executed successfully. Rows affected: {st.session_state.sql_exec_result_df['rows_affected'].iloc[0]}")
                 else:
                     # It was likely a SELECT query that returned no rows
                     st.success("Query executed successfully. No rows returned.")
            else:
                 # Display the DataFrame with results
                 st.dataframe(st.session_state.sql_exec_result_df)
        else:
            # This state might occur if execution was skipped due to LLM error
            st.info("SQL execution was skipped or did not produce results.")
        # --- >>> End Display SQL Execution <<< ---


    # --- Feedback Section ---
    # This section is displayed only if feedback should be shown
    if st.session_state.get('show_feedback', False):
        # ... (Feedback form and submission logic remains the same) ...
        st.divider() # Separator
        st.subheader("Feedback on Generated SQL")
        rating_options = ["Very Bad", "Bad", "OK", "Good", "Very Good"]
        feedback_rating = st.select_slider("Overall rating:", options=rating_options, key="feedback_rating_slider")
        selected_issues = []
        if st.session_state.feedback_rating_slider != "Very Good":
            issue_categories = ["Incorrect Table(s)", "Incorrect Column(s)", "Wrong Aggregation", "Incorrect Filter/WHERE", "Syntax Error", "Doesn't Answer Question", "Other"]
            selected_issues = st.multiselect("Select issue categories (optional):", options=issue_categories, key="feedback_issues_multi")
        feedback_comment = st.text_area("Optional comments:", key="feedback_comment_combo", height=100)

        if st.button("Submit Feedback", key="submit_feedback_button_combo"):
            rating_value = st.session_state.feedback_rating_slider
            issues_value = st.session_state.feedback_issues_multi
            comment_value = st.session_state.feedback_comment_combo
            logger.info(f"Feedback received: Rating='{rating_value}', Issues='{issues_value}', Comment='{comment_value}'")
            logger.info(f"Feedback context: {st.session_state.current_query_context}")
            run_id_to_update = st.session_state.current_query_context.get('mongodb_id')
            if run_id_to_update:
                logger.info(f"Attempting to save feedback for MongoDB ID: {run_id_to_update}")
                try:
                    success = save_feedback(run_id=run_id_to_update, rating=rating_value, issues=issues_value, comment=comment_value)
                    if success:
                        st.success("Thank you for your feedback! (Saved to DB)")
                        st.session_state.show_feedback = False # Hide form
                        st.session_state.results_ready = False # Hide results
                        logger.info(f"Successfully saved feedback for run {run_id_to_update}.")
                        st.rerun() # Force a UI refresh
                    else:
                        st.error("Sorry, there was an issue saving your feedback to the database.")
                        logger.error(f"save_feedback function returned False for run {run_id_to_update}.")
                except Exception as e:
                    logger.error(f"Failed to save feedback to DB for run {run_id_to_update}: {e}", exc_info=True)
                    st.error("Sorry, an unexpected error occurred while saving your feedback.")
            else:
                st.error("Cannot save feedback: Missing the Run ID for the previous query. Please generate SQL again.")
                logger.error("Cannot save feedback: 'mongodb_id' not found in current_query_context.")


# --- Tab 2: Evaluation Analytics ---
# with tab2:
#     st.header("Analyze Experiment Results")
#     st.write("View aggregated metrics and comparisons from completed experiment runs.")
#     st.info("This section will display analytics once experiment data is logged in the database.")

#     st.subheader("Overall Performance Metrics (Placeholder)")
#     st.write("Average EM/ExecAcc scores per prompt type, dataset, etc. will be shown here.")
#     # Placeholder for fetching and displaying aggregated data...

#     st.subheader("Performance Comparison Charts (Placeholder)")
#     st.write("Bar charts comparing prompt techniques or performance across datasets will be displayed here.")
#     # Placeholder for creating charts...


# --- Tab 3: Run History ---
with tab3:
    st.header("Detailed Run History")
    st.write("Browse and search through the logs of individual query runs.")

    # --- Filtering Widgets ---
    st.subheader("Filter History")
    col1, col2, col3 = st.columns(3)
    with col1:
        # Use a key to easily access the value later
        filter_run_id = st.text_input("Filter by Run ID:", key="filter_run_id_input")
    with col2:
        filter_dataset = st.selectbox("Filter by Dataset:", ["All"] + available_datasets, key="hist_dataset_filter")
    with col3:
        filter_prompt_type = st.selectbox("Filter by Prompt Type:", ["All"] + available_prompt_types, key="hist_prompt_filter")
    # ------------------------

    # --- Trigger Fetching ---
    fetch_now = False
    # Check if the search button was clicked
    if st.button("Search History", key="search_history_button"):
        fetch_now = True
        st.session_state.history_loaded = True # Mark that a search was performed
        logger.info(f"Search button clicked. Fetching history with filters: RunID='{st.session_state.filter_run_id_input}', Dataset='{st.session_state.hist_dataset_filter}', Prompt='{st.session_state.hist_prompt_filter}'")
    # Check if history hasn't been loaded yet for the initial view
    elif not st.session_state.history_loaded:
        fetch_now = True
        st.session_state.history_loaded = True # Mark that initial load is happening
        logger.info("Tab 3 first view. Fetching initial history (no filters).")
    # ----------------------

    # --- Fetch Data Logic ---
    if fetch_now:
        with st.spinner("Fetching history..."):
            try:
                # Prepare filter arguments based on whether search was clicked or initial load
                # Use session state keys to get current widget values
                run_id_filter_arg = None
                dataset_filter_arg = None
                prompt_filter_arg = None

                # Only apply filters if the search button was the trigger
                if st.session_state.get("search_history_button"): # Check if button was clicked
                    dataset_filter_arg = None if st.session_state.hist_dataset_filter == "All" else st.session_state.hist_dataset_filter
                    prompt_filter_arg = None if st.session_state.hist_prompt_filter == "All" else st.session_state.hist_prompt_filter
                    run_id_filter_arg = None if not st.session_state.filter_run_id_input else st.session_state.filter_run_id_input

                # Call the actual backend function
                history_list = fetch_run_history(
                    run_id=run_id_filter_arg,
                    dataset=dataset_filter_arg,
                    prompt_type=prompt_filter_arg
                    # limit=50 # Keep the default limit from db_handler
                )

                # Store results (or empty list) in session state
                if history_list:
                    # Convert list of dicts to DataFrame for display
                    st.session_state.history_data = pd.DataFrame(history_list)
                    logger.info(f"Successfully fetched {len(st.session_state.history_data)} history records.")
                else:
                    st.session_state.history_data = pd.DataFrame() # Store empty DataFrame
                    logger.info("No history records found matching the criteria.")

            except Exception as e:
                logger.error(f"Error fetching or processing history: {e}", exc_info=True)
                st.error(f"An error occurred while fetching history: {e}")
                st.session_state.history_data = pd.DataFrame() # Ensure it's an empty DF on error
    # --- End Fetch Data Logic ---

    # --- Display History Data ---
    st.subheader("History Results")
    if st.session_state.history_data is not None:
        if not st.session_state.history_data.empty:
            # Define columns to display initially (adjust as needed)
            display_columns = [
                "_id", "timestamp", "dataset", "prompt_type", "llm",
                "nl_query", "generated_sql", "em_score", "exec_acc_score",
                "duration_sec" # Add other relevant columns from your logged context
            ]
            # Filter DataFrame to only include existing columns among the desired ones
            columns_to_show = [col for col in display_columns if col in st.session_state.history_data.columns]

            st.dataframe(st.session_state.history_data[columns_to_show])
        else:
            # Show message if DataFrame exists but is empty (e.g., after filtering)
             st.write("No matching run history found for the selected criteria.")
    else:
        # Initial state before any loading attempt
        st.write("History will be loaded here. Click 'Search History' or view on initial load.")
    # --- End Display History Data ---