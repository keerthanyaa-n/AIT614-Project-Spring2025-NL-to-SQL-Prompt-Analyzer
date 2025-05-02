# app/main_streamlit.py
import streamlit as st
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
    available_datasets = ["Spider_Dev", "WikiSQL_Test", "RealWorld_SalesDB"]
    available_prompt_types = ["Zero-Shot", "Few-Shot", "Structured/Domain-Specific"]
    available_llms = ["GPT-4 (Placeholder)", "LLaMA-2 (Placeholder)"]

    selected_dataset = st.selectbox("Select Dataset:", available_datasets)
    selected_prompt_type = st.selectbox("Select Prompt Technique:", available_prompt_types)
    selected_llm = st.selectbox("Select LLM:", available_llms)
    st.divider()

# --- Main Area with Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 NL Query Test", "📈 Evaluation Analytics", "📜 Run History"])

# --- Tab 1: Live NL Query Testing ---
with tab1:
    st.header("Test NL Query to SQL Generation")
    st.write("Enter a natural language query and select parameters to generate and evaluate SQL.")

    nl_query = st.text_area("Your question:", height=100, placeholder="e.g., Show me the total sales per region for 'Electronics'.", key="nl_query_input")

    if st.button("Generate SQL", key="generate_sql_button"):
        # Reset state for new query generation attempt
        st.session_state.results_ready = False
        st.session_state.show_feedback = False
        if not nl_query:
            st.warning("Please enter a natural language query.")
            logger.warning("Generate SQL clicked with empty query.") # Log warning

        else:
            
            # --- Log Start Marker and Context ---
            logger.info("--- Begin Generate User Query ---")
            logger.info(f"Parameters: Dataset='{selected_dataset}', PromptType='{selected_prompt_type}', LLM='{selected_llm}'")
            logger.info(f"NL Query: '{nl_query}'")
            # -------------------------------------
            start_time = time.perf_counter()
            # THIS IS THE NEW CODE BLOCK TO USE
            try:
                # --- Call the ACTUAL backend graph ---
                with st.spinner("Running NL2SQL generation graph..."): # Updated spinner message
                    logger.info("Invoking backend graph...") # <<< Will see this log now

                    # Call the entry point function from graph_logic/graph.py
                    graph_result_state = run_nl2sql_graph(
                        nl_query=nl_query,                     # Input from text area
                        prompt_strategy=selected_prompt_type,  # Input from dropdown
                        selected_llm=selected_llm              # Input from dropdown
                    )

                    logger.info("Backend graph execution attempt complete.") # <<< Will see this log

                    # Extract results and check for errors from the graph
                    generated_sql = graph_result_state.get("generated_sql")
                    prompt = graph_result_state.get("final_prompt", "Prompt not captured by graph state.")
                    graph_error = graph_result_state.get("error")

                    # --- Handle graph execution errors ---
                    if graph_error:
                        raise Exception(f"Backend graph execution failed: {graph_error}")
                    if not generated_sql:
                         raise Exception("Graph execution finished but no SQL was generated (check logs).")

                # --- Placeholder for Evaluation (using results from graph) ---
                em_score = "N/A" # Initialize
                exec_acc_score = "N/A" # Initialize
                current_ground_truth = st.session_state.ground_truth_input # Get GT
                if current_ground_truth:
                    logger.info("Proceeding to placeholder evaluation.")
                    # Placeholder: Replace with actual call later
                    # eval_results = evaluate_sql(generated_sql, current_ground_truth, db_conn)
                    em_score = "0.0 (Eval Placeholder)"
                    exec_acc_score = "0.0 (Eval Placeholder)"
                else:
                    logger.info("No ground truth provided, skipping evaluation step.")
                # -------------------------------------------------------------

                end_time = time.perf_counter() # Calculate duration AFTER graph runs
                duration = end_time - start_time
                st.success(f"Processing complete in {duration:.3f} seconds!") # <<< Updated success message

                # --- Store results in session state ---
                # (This part should be correct from previous steps, uses variables like prompt, generated_sql, em_score etc.)
                st.session_state.last_prompt = prompt
                st.session_state.last_sql = generated_sql
                st.session_state.last_em_score = em_score
                st.session_state.last_exec_acc_score = exec_acc_score
                st.session_state.last_duration = duration
                st.session_state.results_ready = True
                st.session_state.show_feedback = True
                st.session_state.current_query_context = {
                    # ... (populate context dictionary as before) ...
                     "nl_query": nl_query, "dataset": selected_dataset, "prompt_type": selected_prompt_type,
                     "llm": selected_llm, "generated_sql": generated_sql, "prompt": prompt,
                     "ground_truth_sql": current_ground_truth, "em_score": em_score,
                     "exec_acc_score": exec_acc_score, "duration_sec": duration, "graph_error": graph_error
                }

                # --- Log Results (Simulated DB Call for now) ---
                logger.info("Logging results to database (Simulated Call)...") # Keep simulation here for now
                logger.debug(f"Result Context for Logging: {st.session_state.current_query_context}")
                # Replace with: result_id = log_result(**st.session_state.current_query_context)
                st.info("Results logged (simulated DB call).")


            except Exception as e:
                # Catch errors from graph call or subsequent processing
                st.session_state.results_ready = False
                st.session_state.show_feedback = False
                end_time = time.perf_counter()
                duration = end_time - start_time
                logger.error(f"An error occurred in 'Run Generation & Evaluation': {e}", exc_info=True)
                st.error(f"An error occurred: {e}")
                st.caption(f"Processing time before error: {duration:.3f} seconds")
            finally:
                 logger.info("--- End Generate User Query Attempt ---") # Add a clear end marker
                    # --------------------------


    # --- Display Results Area (Conditional based on session state) ---
    # This section now runs on *every* rerun, displaying results if they are marked ready
    if st.session_state.get('results_ready', False):
        st.markdown("---") # Add a separator
        st.subheader("Generated Output")
        st.text_area("Generated Prompt:", st.session_state.last_prompt, height=150, key="prompt_display_state", disabled=True) # Disable to prevent edits
        st.text_area("Generated SQL:", st.session_state.last_sql, height=150, key="sql_display_state", disabled=True) # Disable to prevent edits
        st.markdown(f"**Evaluation (Placeholders for this query):**")
        st.write(f"- Exact Match (EM) Score: {st.session_state.last_em_score}")
        st.write(f"- Execution Accuracy (ExecAcc) Score: {st.session_state.last_exec_acc_score}")
        st.caption(f"Processing time: {st.session_state.last_duration:.3f} seconds")

    

    # --- Feedback Section (Conditional based on session state) ---
    # This condition is checked independently of results display
    if st.session_state.get('show_feedback', False):
        st.divider()
        st.subheader("Feedback on Generated SQL")

        # Using Option 3 (Combination) from previous suggestions
        rating_options = ["Very Bad", "Bad", "OK", "Good", "Very Good"]
        feedback_rating = st.select_slider(
            "Overall rating:",
            options=rating_options,
            key="feedback_rating_slider" # Session state handles value persistence
        )

        selected_issues = [] # Default to empty list
        if st.session_state.feedback_rating_slider != "Very Good": # Check state directly
            issue_categories = [
                "Incorrect Table(s)", "Incorrect Column(s)", "Wrong Aggregation",
                "Incorrect Filter/WHERE", "Syntax Error", "Doesn't Answer Question", "Other"
            ]
            selected_issues = st.multiselect(
                "Select issue categories (optional):",
                options=issue_categories,
                key="feedback_issues_multi" # Session state handles value persistence
            )

        feedback_comment = st.text_area(
            "Optional comments (corrections, explanations):",
            key="feedback_comment_combo", # Session state handles value persistence
            height=100
        )

        if st.button("Submit Feedback", key="submit_feedback_button_combo"):
            # Log and save feedback using values directly from session state keys
            rating_value = st.session_state.feedback_rating_slider
            issues_value = st.session_state.feedback_issues_multi
            comment_value = st.session_state.feedback_comment_combo

            # Logging functions
            logger.info("Displaying generated output to the user.")
            logger.info(f"Scores: EM={st.session_state.last_em_score}, ExecAcc={st.session_state.last_exec_acc_score}. Duration={st.session_state.last_duration:.3f}s")
            
            logger.info(f"Feedback received: Rating='{rating_value}', Issues='{issues_value}', Comment='{comment_value}'")
            logger.info(f"Feedback context: {st.session_state.current_query_context}")

            try:
                # save_feedback(...) using rating_value, issues_value, comment_value
                st.success("Thank you for your feedback! (Saved - simulated)")
                st.session_state.show_feedback = False # Hide form
                st.session_state.results_ready = False # Also hide results? Or keep them? Decide behaviour. Let's hide results too.
                # Reset feedback widgets for next time (optional, rerun helps)
                ### UNCOMMENT BELOW 
                # st.session_state.feedback_rating_slider = "OK"
                # st.session_state.feedback_issues_multi = []
                # st.session_state.feedback_comment_combo = ""
                ### UNCOMMENT ABOVE
                logger.info("Feedback Saved.")
                logger.info("---END of Generate SQL Query---")

            except Exception as e:
                logger.error(f"Failed to save feedback: {e}", exc_info=True)
                st.error("Sorry, there was an issue saving your feedback.")

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
    st.write("Browse and search through the logs of individual query runs or experiment results.")
    st.info("This section will display detailed logs once data is available in the database.")

    st.subheader("Filter History (Placeholder)")
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_run_id = st.text_input("Filter by Run ID:")
    with col2:
        filter_dataset = st.selectbox("Filter by Dataset:", ["All"] + available_datasets, key="hist_dataset_filter")
    with col3:
        filter_prompt_type = st.selectbox("Filter by Prompt Type:", ["All"] + available_prompt_types, key="hist_prompt_filter")

    # --- Search Button ---
    if st.button("Search History", key="search_history_button"): # <<< Add search button
        logger.info(f"Searching history with filters: RunID='{filter_run_id}', Dataset='{filter_dataset}', Prompt='{filter_prompt_type}'")
        st.info("Fetching history based on filters... (Placeholder)")

        # --- Fetch and Display Logic (Inside Button Click) ---
        try:
            # Prepare filter arguments for the backend function
            # Handle "All" selections by passing None or omitting the filter
            dataset_filter_arg = None if filter_dataset == "All" else filter_dataset
            prompt_filter_arg = None if filter_prompt_type == "All" else filter_prompt_type
            run_id_filter_arg = None if not filter_run_id else filter_run_id # Pass None if empty

            # Placeholder: Replace with actual call to your db_handler function
            # run_logs_df = fetch_run_history(
            #     run_id=run_id_filter_arg,
            #     dataset=dataset_filter_arg,
            #     prompt_type=prompt_filter_arg
            # ) # Needs implementation

            # Simulate fetching data for demonstration
            st.write(f"Simulating fetch with filters: RunID={run_id_filter_arg}, Dataset={dataset_filter_arg}, Prompt={prompt_filter_arg}")
            # Create a dummy DataFrame for placeholder display
            dummy_data = {
                'timestamp': [pd.Timestamp.now()],
                'run_id': [run_id_filter_arg if run_id_filter_arg else 'N/A'],
                'dataset_name': [dataset_filter_arg if dataset_filter_arg else 'Any'],
                'prompt_type': [prompt_filter_arg if prompt_filter_arg else 'Any'],
                'nl_question_text': ['Placeholder question based on filter...'],
                'generated_sql': ['SELECT placeholder...'],
                'em_score': [0.0], 'exec_acc_score': [0.0]
                }
            run_logs_df = pd.DataFrame(dummy_data)
            # -------------------------------------------

            st.subheader("Filtered Results")
            if run_logs_df is not None and not run_logs_df.empty:
                st.dataframe(run_logs_df) # Display the detailed dataframe
                logger.info(f"Displayed {len(run_logs_df)} history records.")
            else:
                st.write("No matching run history found in the database for the selected filters.")
                logger.info("No matching history records found.")

        except Exception as e:
            logger.error(f"Error fetching or displaying history: {e}", exc_info=True)
            st.error(f"An error occurred while fetching history: {e}")

    else:
        # Optionally display a message prompting the user to click the button
        st.write("Enter filter criteria above and click 'Search History'.")