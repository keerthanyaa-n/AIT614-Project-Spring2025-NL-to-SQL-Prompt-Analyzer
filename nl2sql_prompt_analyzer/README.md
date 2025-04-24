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
├── core/             # Core logic for the NL2SQL process
│   ├── prompt_generator.py # Logic for creating different prompt types
│   ├── llm_interface.py    # Wrapper for interacting with LLMs
│   ├── sql_executor.py     # Logic for validating and executing SQL queries
│   └── evaluator.py        # Logic for calculating EM and ExecAcc scores
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
├── logs/             # Directory where .log files are written
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