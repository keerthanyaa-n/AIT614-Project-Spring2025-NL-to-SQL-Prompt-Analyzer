# NL2SQL Prompt Engineering Analyzer

## Description

This project is an analysis and evaluation framework designed to systematically study the impact of various prompt engineering techniques on the accuracy of SQL query generation by Large Language Models (LLMs). It focuses on the Natural Language to SQL (NL2SQL) task, comparing model performance across standard benchmark datasets (like Spider, WikiSQL) and simulated real-world database scenarios which often feature unstructured schemas and domain-specific ambiguities.

The framework allows users to input natural language questions, apply different prompting strategies (Zero-Shot, Few-Shot, Structured/Domain-Specific [, Chain-of-Thought - TBC]), generate SQL queries using configurable LLMs (e.g., GPT, LLaMA), execute these queries, and evaluate their accuracy using metrics like Exact Match (EM) and Execution Accuracy (ExecAcc).

*(Based on the project proposal dated approx. April 2025, Fairfax, VA)*

## Objectives

* Explain how different prompt engineering techniques influence SQL query generation accuracy in NL2SQL models.
* Compare the performance of NL2SQL models on benchmark datasets versus real-world databases.
* Identify optimal prompt strategies for increasing query accuracy and model generalization.
* Provide insights into the real-world usability and robustness of NL2SQL models in practical business environments.

## Directory Structure

```
nl2sql_prompt_analyzer/
│
├── app/              # Contains the main Streamlit user interface code
│   └── main_streamlit.py # Entry point for the Streamlit application
│
├── data_handling/    # Utilities for loading datasets and schemas
│   ├── dataset_loader.py   # Functions to load/access dataset info
│   └── schema_utils.py     # Functions to fetch/format schema data for prompts
│
├── storage/          # Handles interaction with the database (SQL)
│   └── db_handler.py       # Functions for database operations (CRUD for logs, results, etc.)
│
├── experiments/      # Scripts for running automated batch experiments
│   └── run_experiments.py  # Main script to run evaluation batches
├── graph_logic/          # <<< NEW DIRECTORY FOR LANGGRAPH COMPONENTS
│   ├── __init__.py
│   ├── state.py          # Defines the graph state
│   ├── prompts.py        # Prompt templates/logic
│   ├── schema.py         # Schema fetching/formatting
│   ├── sql_gen.py        # Node for calling LLM to generate SQL
│   └── graph.py          # Node definitions and graph assembly
│
├── analysis/         # Jupyter notebooks or scripts for analyzing results
│   └── result_analyzer.ipynb # Example notebook for analysis
│
├── config/           # Configuration files
│   ├── settings.py         # Stores API keys, DB connection strings, model params
│   └── logging_config.py   # Configures application logging
│
├── tests/            # Unit and integration tests (Optional)
│
├── logs/             # Directory where .log files are written local logs (during development, can be removed later)
│
├── datasets/         # Placeholder for storing small datasets or schema files
│
├── requirements.txt  # Project dependencies
├── README.md         # This file
└── .gitignore        # Specifies intentionally untracked files for Git
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd nl2sql_prompt_analyzer
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows (cmd)
    python -m venv venv
    venv\Scripts\activate.bat

    # Windows (PowerShell)
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You need to add necessary packages like `streamlit`, database drivers, LLM SDKs, etc., to `requirements.txt`)*

4.  **Configure Settings:**
    * Update `config/settings.py` with your LLM API keys and database connection details (once the DB setup is complete).

## Usage

To run the main user interface:

```bash
streamlit run app/main_streamlit.py
```

This will start the Streamlit server, and you can access the application through your web browser at the displayed local URL.

Logging
Application logs (including errors and informational messages) are configured in config/logging_config.py and are written to the logs/ directory (e.g., logs/nl2sql_analyzer.log) and also displayed on the console.

## Working Components

This section describes parts of the application that are implemented and functional, even if some underlying operations (like LLM calls or DB saves) are currently simulated.

### Streamlit Interface (`app/main_streamlit.py`)

* **Entry Point:** The application is launched via `streamlit run app/main_streamlit.py`.

* **Layout:** Features a wide layout with:
    * A **Sidebar** for global configuration (selecting Dataset, Prompt Technique, LLM) and for entering optional Ground Truth SQL for evaluation purposes.
    * A **Main Area** organized into Tabs: "NL Query Test", "Evaluation Analytics" (placeholder), and "Run History" (placeholder).

* **NL Query Test Tab:**
    * Allows users to input a natural language query.
    * A button ("Run Generation & Evaluation") triggers the backend LangGraph workflow.
    * Displays a loading spinner during processing.
    * Shows the generated Prompt and the (currently simulated) SQL output received from the graph.
    * Displays placeholder Evaluation Scores (EM/ExecAcc).
    * Includes an interactive **Feedback Section** (rating slider, issue selection, comments) that appears after generation; submitting feedback logs the input and context (simulated save).

* **State Management:** Utilizes `st.session_state` to maintain user inputs, configuration selections, generated results, and UI visibility across interactions.

### Logging of Step-by-Step Process

* **Configuration:** Logging is configured via `config/logging_config.py`, setting up formatters and handlers (typically console and potentially file output to the `logs/` directory).

* **Execution Trace:** Detailed logs (`INFO`, `DEBUG`, `ERROR`) are generated throughout the application flow:
    * Records user selections (Dataset, Prompt, LLM) and the input NL query when generation is triggered.
    * Logs the invocation of the backend LangGraph workflow (`run_nl2sql_graph`).
    * Traces execution within the LangGraph graph, logging entry into key nodes (`route_preparation`, specific `fetch_..._prompt` nodes, `call_llm_node`).
    * Shows the routing decision made based on the selected prompt strategy.
    * Logs details of the (currently simulated) LLM interaction within `sql_gen.py`, including which LLM client class was instantiated.
    * Captures submitted feedback details and the associated query context.
    * Records any errors encountered during graph execution or Streamlit processing.
* **Purpose:** Provides essential visibility for debugging and understanding the step-by-step execution path, including the conditional logic flow within the LangGraph agent.



## ToDO 
1. Connect to mongo DB 
2. test MongoDB connection, with sample feedback values being pushed in to MongoDB 
3. Add langgraph nodes 
4. Add LLM nodes to depict sample Node flows 
5. Error handling
6. testing the above pointers
7. LLM selection
8. DB creation 
9. INtegrate Prompts 
10. test and evaluate. 
