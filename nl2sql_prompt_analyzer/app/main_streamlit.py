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
# from core.prompt_generator import generate_prompt
# from core.llm_interface import query_llm
# from core.evaluator import evaluate_sql
# from storage.db_handler import get_datasets, log_result, fetch_evaluation_results, fetch_run_history # Examples
# -----------------------------------------------

# --- Setup Logging ---
setup_logging()
logger = logging.getLogger(__name__)
# ---------------------


# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("NL2SQL Prompt Engineering Analyzer")

logger.info("Streamlit app started.")

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
        if not nl_query:
            st.warning("Please enter a natural language query.")
        else:
            logger.info(f"Generating SQL for query: '{nl_query}' using {selected_prompt_type} on {selected_dataset} with {selected_llm}")

            start_time = time.perf_counter() # <<< Start timer
            prompt = None
            generated_sql = None
            em_score = "N/A"
            exec_acc_score = "N/A"

            try:
                # Wrap the core logic in a spinner
                with st.spinner("Generating SQL query... Please wait."): # <<< Add spinner
                    # --- 1. Generate Prompt (Placeholder) ---
                    logger.debug(f"Generating prompt using type: {selected_prompt_type}")
                    # prompt = generate_prompt(nl_query, selected_prompt_type, selected_dataset) # Replace with actual call
                    prompt = f"Placeholder prompt for '{nl_query}' using {selected_prompt_type} on {selected_dataset}"
                    logger.debug("Prompt generation placeholder complete.")

                    # --- 2. Query LLM (Placeholder) ---
                    logger.debug(f"Querying LLM: {selected_llm}")
                    # generated_sql = query_llm(prompt, selected_llm) # Replace with actual call
                    generated_sql = f"SELECT 'placeholder_sql' FROM {selected_dataset} WHERE condition = '{nl_query[:20]}...';"
                    logger.debug("LLM query placeholder complete.")

                    # --- Simulate backend processing time ---
                    time.sleep(3) # <<< Simulate 3 seconds delay
                    # -----------------------------------------

                    # --- 3. Evaluate SQL (Placeholder) ---
                    # This would happen after generation in a real scenario, kept here for placeholder structure
                    logger.debug("Evaluating SQL (Placeholder - requires ground truth)")
                    em_score = "N/A (Needs Ground Truth)"
                    exec_acc_score = "N/A (Needs Ground Truth & Execution)"
                    logger.debug("Evaluation placeholder complete.")

                # --- End of spinner ---

                end_time = time.perf_counter() # <<< End timer
                duration = end_time - start_time # <<< Calculate duration

                st.success("Processing complete!") # Indicate spinner finished

                # --- Display results ---
                st.text_area("Generated Prompt:", prompt, height=150, key="prompt_display")
                st.text_area("Generated SQL:", generated_sql, height=150, key="sql_display")
                st.markdown(f"**Evaluation (Placeholders for this query):**")
                st.write(f"- Exact Match (EM) Score: {em_score}")
                st.write(f"- Execution Accuracy (ExecAcc) Score: {exec_acc_score}")
                st.caption(f"Processing time: {duration:.3f} seconds") # <<< Display processing time

                # --- 4. Log Results (Placeholder) ---
                logger.debug("Logging results to database (Placeholder)")
                # log_result(..., latency_ms=int(duration*1000)) # Include duration when logging
                st.info("Results logged (simulated).")


            except Exception as e:
                end_time = time.perf_counter() # Still record end time on error if possible
                duration = end_time - start_time
                logger.error(f"An error occurred: {e}", exc_info=True) # Log full traceback
                st.error(f"An error occurred during processing: {e}")
                st.caption(f"Processing time before error: {duration:.3f} seconds")

        # --- Feedback Section (Conditional Display) ---
        if st.session_state.get('show_feedback', False):
            st.divider()
            st.subheader("Feedback on Generated SQL")

            # Use columns for layout if needed, radio is often fine on its own
            feedback_rating = st.radio(
                "Rate the generated SQL:",
                ("Good 👍", "Bad 👎", "Not Sure"),
                key="feedback_rating",
                horizontal=True,
                index=None # Nothing selected by default
            )

            feedback_comment = st.text_area(
                "Optional comments (e.g., why it was good/bad, suggested correction):",
                key="feedback_comment",
                height=100
            )

            if st.button("Submit Feedback", key="submit_feedback_button"):
                if feedback_rating is None:
                    st.warning("Please select a rating (Good/Bad/Not Sure).")
                else:
                    # Log feedback
                    logger.info(f"Feedback received: Rating='{feedback_rating}', Comment='{feedback_comment}'")
                    logger.info(f"Feedback context: {st.session_state.current_query_context}") # Log context

                    # Placeholder for saving feedback
                    try:
                        # save_feedback(
                        #     context=st.session_state.current_query_context, # Pass context
                        #     rating=feedback_rating,
                        #     comment=feedback_comment
                        # ) # Needs implementation in db_handler
                        st.success("Thank you for your feedback! (Saved - simulated)")
                        # Hide the form after successful submission
                        st.session_state.show_feedback = True
                        # Clear the widgets for the next run (Streamlit might handle this on rerun)
                        st.session_state.feedback_rating = None
                        st.session_state.feedback_comment = ""
                        st.experimental_rerun() # Force rerun to clear widgets cleanly

                    except Exception as e:
                        logger.error(f"Failed to save feedback: {e}", exc_info=True)
                        st.error("Sorry, there was an issue saving your feedback.")

# --- Tab 2: Evaluation Analytics ---
with tab2:
    st.header("Analyze Experiment Results")
    st.write("View aggregated metrics and comparisons from completed experiment runs.")
    st.info("This section will display analytics once experiment data is logged in the database.")

    st.subheader("Overall Performance Metrics (Placeholder)")
    st.write("Average EM/ExecAcc scores per prompt type, dataset, etc. will be shown here.")
    # Placeholder for fetching and displaying aggregated data...

    st.subheader("Performance Comparison Charts (Placeholder)")
    st.write("Bar charts comparing prompt techniques or performance across datasets will be displayed here.")
    # Placeholder for creating charts...


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