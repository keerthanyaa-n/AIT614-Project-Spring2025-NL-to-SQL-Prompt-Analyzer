# graph_logic/sql_gen.py
from .state import GraphState
import time
import logging
import os
import re
from typing import Protocol, Dict, Type , Optional# For type hinting

# --- Potentially load configurations ---
# from config.settings import OPENAI_API_KEY, GOOGLEAPI_TOKEN # Example

logger = logging.getLogger(__name__)

# ---Imports for LLM calls---
from openai import OpenAI, OpenAIError, APIConnectionError, RateLimitError, APIStatusError
import google.generativeai as genai
import google.generativeai.types as genai_types

# ---Imports for Validation
from pydantic import BaseModel, field_validator, ValidationError

# --- Load .env file ---
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / 'config' / '.env'
if env_path.is_file():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    logging.warning(f".env file not found at {env_path}. Relying on system environment variables.")
# --------------------

# --- Pydantic Model for Basic SQL Validation ---
class SQLQueryValidator(BaseModel):
    """Basic validator to check if a string looks like a SQL query."""
    query: str

    @field_validator('query')
    @classmethod
    def check_sql_start(cls, v: str) -> str:
        """Check if the query starts with common SQL keywords."""
        v_stripped = v.strip()
        # Basic check for common SQL starting keywords (case-insensitive)
        sql_starters = r'^(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|WITH|SHOW)\b'
        if not re.match(sql_starters, v_stripped, re.IGNORECASE):
            raise ValueError('Query does not start with a common SQL keyword (SELECT, INSERT, etc.)')
        # Optional: Add more checks (e.g., presence of FROM/WHERE for SELECT)
        # if v_stripped.upper().startswith('SELECT') and 'FROM' not in v_stripped.upper():
        #     raise ValueError('SELECT query likely missing FROM clause')
        return v # Return original if valid (or potentially v_stripped)


# --- 1. Define the LLM Client Interface (Protocol) ---
class LLMClient(Protocol):
    """Defines the interface for LLM clients used in SQL generation."""

    def __init__(self, config: Dict | None = None):
        """Initialize the client (e.g., with API keys from config)."""
        ...

    def generate_sql(self, prompt: str) -> str:
        """Takes a prompt string and returns the generated SQL string."""
        ...

# --- 2. Implement Concrete LLM Client Classes ---

class MockLLMClient:
    """A mock client for testing without real API calls."""
    def __init__(self, config: Dict | None = None):
        logger.info(f"Initializing MockLLMClient (Config: {config})")
        self.config = config or {}

    def generate_sql(self, prompt: str) -> str:
        logger.info(f"MockLLMClient received prompt (first 50 chars): {prompt[:50]}...")
        # Simulate processing time
        time.sleep(1.5)
        # Return predictable mock SQL
        mock_sql = f"-- MOCK SQL generated --\nSELECT mock_col FROM mock_table WHERE input LIKE '%{prompt[-20:]}%';"
        logger.info("MockLLMClient returning simulated SQL.")
        return mock_sql

class OpenAIClient:
    """Client for interacting with OpenAI models (e.g., gpt-4o-mini)."""
    def __init__(self, config: Optional[Dict] = None):
        logger.info("Initializing OpenAIClient...")
        self.config = config or {}
        self.model_name = self.config.get("model", "gpt-4o-mini") # Default to gpt-4o-mini

        if OpenAI is None or OpenAIError is None:
             logger.error("OpenAI library not installed.")
             raise ImportError("openai library is required for OpenAIClient.")
        if BaseModel is None: # Check if Pydantic is available
             logger.error("Pydantic library not installed.")
             raise ImportError("pydantic library is required for SQL validation.")

        try:
            # CLARIFICATION: OpenAI() implicitly reads the OPENAI_API_KEY environment variable
            self.client = OpenAI()
            self.client.models.list() # Simple call to check authentication
            logger.info(f"OpenAI client initialized successfully for model {self.model_name}.")
        except (OpenAIError, APIConnectionError) as e:
            logger.error(f"Failed to initialize or authenticate OpenAI client: {e}", exc_info=False)
            self.client = None
            raise ConnectionError(f"Failed to connect/authenticate OpenAI: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI client initialization: {e}", exc_info=True)
            self.client = None
            raise ConnectionError(f"Unexpected error initializing OpenAI: {e}")

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Internal helper to make the ChatCompletion call and handle common logic."""
        if not self.client: return "-- ERROR: OpenAI client not initialized."
        logger.debug(f"Sending to OpenAI:\nSystem: {system_prompt}\nUser: {user_prompt}")
        try:
            response = self.client.chat.completions.create(
                model=self.model_name, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], temperature=0.1)
            # Log Token Usage
            if response.usage: logger.info(f"OpenAI API Usage: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}, Total={response.usage.total_tokens} tokens.")
            else: logger.warning("Token usage info missing.")

            if response.choices:
                raw_text = response.choices[0].message.content.strip()
                logger.debug(f"Raw response from OpenAI: {raw_text}")
                # Clean markdown fences
                if raw_text.lower().startswith("```sql"): raw_text = raw_text[6:]
                if raw_text.lower().startswith("```"): raw_text = raw_text[3:]
                if raw_text.endswith("```"): raw_text = raw_text[:-3]
                cleaned_text = raw_text.strip()
                logger.info("Successfully received response from OpenAI.")
                return cleaned_text
            else:
                finish_reason = response.choices[0].finish_reason if response.choices else 'N/A'; logger.warning(f"OpenAI no choices. Finish reason: {finish_reason}"); return f"-- WARNING: OpenAI no choices (Reason: {finish_reason})."
        # Error Handling
        except RateLimitError as e: logger.error(f"OpenAI Rate Limit: {e}"); return f"-- ERROR: OpenAI Rate Limit."
        except APIConnectionError as e: logger.error(f"OpenAI Connection Error: {e}"); return f"-- ERROR: OpenAI Connection Error."
        except APIStatusError as e: logger.error(f"OpenAI Status Error: {e}"); return f"-- ERROR: OpenAI Status Error: {e.status_code}"
        except OpenAIError as e: logger.error(f"OpenAI API Error: {e}", exc_info=True); return f"-- ERROR: OpenAI API Error."
        except Exception as e: logger.error(f"OpenAI Unexpected Error: {e}", exc_info=True); return f"-- ERROR: Unexpected OpenAI call error."

    def generate_sql(self, prompt: str) -> str:
        """Generates SQL using the configured OpenAI model, logs tokens, and validates output."""
        if not self.client:
            logger.error("OpenAI client not initialized.")
            return "-- ERROR: OpenAI client not initialized."

        logger.info(f"Querying OpenAI model '{self.model_name}'...")
        system_prompt = "You are an expert SQL generator. Generate only the SQL query."
        user_prompt = prompt

        logger.debug(f"Sending to OpenAI:\nSystem: {system_prompt}\nUser: {user_prompt}")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
            )
            logger.info(f"OpenAI raw response : {response}")
            # --- >>> Log Token Usage <<< ---
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                logger.info(f"OpenAI API Usage: Prompt={prompt_tokens}, Completion={completion_tokens}, Total={total_tokens} tokens.")
            else:
                logger.warning("Token usage information not available in OpenAI response.")
            # --- >>> End Token Logging <<< ---

            if response.choices:
                raw_sql = response.choices[0].message.content.strip()
                logger.debug(f"Raw response from OpenAI: {raw_sql}")

                # Clean potential markdown code fences first
                if raw_sql.lower().startswith("```sql"): raw_sql = raw_sql[6:]
                if raw_sql.endswith("```"): raw_sql = raw_sql[:-3]
                cleaned_sql = raw_sql.strip()

                # --- >>> Validate SQL using Pydantic <<< ---
                try:
                    SQLQueryValidator(query=cleaned_sql)
                    logger.info("Generated SQL passed basic validation.")
                    return cleaned_sql # Return validated and cleaned SQL
                except ValidationError as val_err:
                    logger.error(f"Generated text failed SQL validation: {val_err}")
                    logger.error(f"Invalid SQL received: {cleaned_sql}")
                    return f"-- ERROR: Generated text failed SQL validation: {val_err}. Output was: {cleaned_sql}"
                # --- >>> End Validation <<< ---

            else:
                finish_reason = response.choices[0].finish_reason if response.choices else 'N/A'
                logger.warning(f"OpenAI response contained no choices. Finish reason: {finish_reason}")
                return f"-- WARNING: OpenAI returned no response choices (Finish Reason: {finish_reason})."

        except RateLimitError as e:
             logger.error(f"OpenAI API rate limit exceeded: {e}", exc_info=False)
             return f"-- ERROR: OpenAI API Rate Limit Exceeded. Please try again later."
        except APIConnectionError as e:
             logger.error(f"OpenAI API connection error: {e}", exc_info=False)
             return f"-- ERROR: OpenAI API Connection Error: {e}"
        except APIStatusError as e:
             logger.error(f"OpenAI API status error (e.g., 4xx, 5xx): {e}", exc_info=False)
             return f"-- ERROR: OpenAI API Status Error: Status={e.status_code}, Message={e.message}"
        except OpenAIError as e:
            logger.error(f"OpenAI API error during SQL generation: {e}", exc_info=True)
            return f"-- ERROR: OpenAI API Error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error during OpenAI SQL generation: {e}", exc_info=True)
            return f"-- ERROR: Unexpected error during OpenAI call: {e}"
        
    def predict_tables(self, prompt: str) -> str:
        """Predicts relevant tables using OpenAI model. Returns cleaned text or error string."""
        logger.info(f"Calling OpenAI model '{self.model_name}' for table prediction.")
        # System prompt specific to table prediction
        system_prompt = "You are an assistant that identifies relevant database tables based on a user query and table descriptions. List only the names of the relevant tables, separated by commas. If no tables seem relevant, output 'None'."
        # The user prompt here is the one constructed by generate_table_prediction_prompt
        user_prompt = prompt
        return self._call_openai(system_prompt=system_prompt, user_prompt=user_prompt)



# --- Updated Gemini Client with REAL API Call ---
class GeminiClient:
    """Client for interacting with Google Gemini models (e.g., gemini-1.5-flash-latest)."""
    def __init__(self, config: Optional[Dict] = None):
        logger.info("Initializing GeminiClient...")
        self.config = config or {}
        self.model_name = self.config.get("model", "gemini-1.5-flash-latest") # Default to Flash

        if genai is None or genai_types is None:
            logger.error("google-generativeai library not installed.")
            raise ImportError("google-generativeai library is required for GeminiClient.")
        if BaseModel is None: # Check if Pydantic is available
             logger.error("Pydantic library not installed.")
             raise ImportError("pydantic library is required for SQL validation.")

        try:
            api_key = os.environ.get('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables or .env file.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini client initialized successfully for model {self.model_name}.")
        except ValueError as e:
             logger.error(f"Gemini configuration error (likely API key issue): {e}", exc_info=False)
             self.model = None
             raise ConnectionError(f"Gemini configuration error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during Gemini client initialization: {e}", exc_info=True)
            self.model = None
            raise ConnectionError(f"Unexpected error initializing Gemini: {e}")
        
    def _call_gemini(self, full_prompt: str) -> str:
        """Internal helper to make the Gemini API call."""
        if not self.model: return "-- ERROR: Gemini model not initialized."
        logger.debug(f"Sending to Gemini:\n{full_prompt}")
        generation_config = genai.types.GenerationConfig(temperature=0.1)
        safety_settings = {}
        try:
            response = self.model.generate_content(full_prompt, generation_config=generation_config, safety_settings=safety_settings)
            # Log Token Usage
            if hasattr(response, 'usage_metadata') and response.usage_metadata: logger.info(f"Gemini API Usage: Prompt={response.usage_metadata.prompt_token_count}, Completion={response.usage_metadata.candidates_token_count}, Total={response.usage_metadata.total_token_count} tokens.")
            else: logger.warning("Token usage metadata missing.")

            # Safely access text
            raw_text = response.text.strip()
            logger.debug(f"Raw response from Gemini: {raw_text}")
            # Clean markdown
            if raw_text.lower().startswith("```sql"): raw_text = raw_text[6:]
            if raw_text.lower().startswith("```"): raw_text = raw_text[3:]
            if raw_text.endswith("```"): raw_text = raw_text[:-3]
            cleaned_text = raw_text.strip()
            logger.info("Successfully received response from Gemini.")
            return cleaned_text

        except genai_types.BlockedPromptException as e:
            logger.error(f"Gemini prompt was blocked: {e}")
            # Try to log feedback if response object exists
            try:
                if response and response.prompt_feedback:
                     logger.error(f"Gemini Block Feedback: {response.prompt_feedback}")
            except Exception: pass # Ignore errors trying to get feedback
            return f"-- ERROR: Gemini prompt blocked."
        except genai_types.StopCandidateException as e:
             logger.error(f"Gemini generation stopped unexpectedly: {e}")
             return f"-- WARNING: Gemini generation stopped unexpectedly (StopCandidateException)."
        except Exception as e:
            logger.error(f"Gemini Unexpected Error: {e}", exc_info=True)
            return f"-- ERROR: Unexpected Gemini call error."

    def generate_sql(self, prompt: str) -> str:
        """Generates SQL using the configured Gemini model, logs tokens (if available), and validates output."""
        if not self.model:
            logger.error("Gemini model not initialized.")
            return "-- ERROR: Gemini model not initialized."

        logger.info(f"Querying Gemini model '{self.model_name}'...")
        full_prompt = prompt
        logger.debug(f"Sending to Gemini:\n{full_prompt}")

        generation_config = genai.types.GenerationConfig(temperature=0.1)
        safety_settings = { } # Use default safety settings initially

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            logger.info(f"Gemini raw response : {response}")
            # --- >>> Log Token Usage (if available) <<< ---
            # Note: Token count might be in response.usage_metadata
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                 prompt_tokens = response.usage_metadata.prompt_token_count
                 completion_tokens = response.usage_metadata.candidates_token_count
                 total_tokens = response.usage_metadata.total_token_count
                 logger.info(f"Gemini API Usage: Prompt={prompt_tokens}, Completion={completion_tokens}, Total={total_tokens} tokens.")
            else:
                 logger.warning("Token usage metadata not available in Gemini response.")
            # --- >>> End Token Logging <<< ---

            # Safely access text using response.text accessor
            raw_sql = response.text.strip()
            logger.debug(f"Raw response from Gemini: {raw_sql}")

            # Clean potential markdown code fences first
            if raw_sql.lower().startswith("```sql"): raw_sql = raw_sql[6:]
            if raw_sql.endswith("```"): raw_sql = raw_sql[:-3]
            cleaned_sql = raw_sql.strip()

            # --- >>> Validate SQL using Pydantic <<< ---
            try:
                SQLQueryValidator(query=cleaned_sql)
                logger.info("Generated SQL passed basic validation.")
                return cleaned_sql # Return validated and cleaned SQL
            except ValidationError as val_err:
                logger.error(f"Generated text failed SQL validation: {val_err}")
                logger.error(f"Invalid SQL received: {cleaned_sql}")
                return f"-- ERROR: Generated text failed SQL validation: {val_err}. Output was: {cleaned_sql}"
            # --- >>> End Validation <<< ---


        except genai_types.BlockedPromptException as e:
            logger.error(f"Gemini prompt was blocked: {e}", exc_info=False)
            try: logger.error(f"Gemini Block Feedback: {response.prompt_feedback}")
            except: pass
            return f"-- ERROR: Gemini prompt blocked."
        except genai_types.StopCandidateException as e:
             logger.error(f"Gemini generation stopped unexpectedly: {e}", exc_info=False)
             reason = "Unknown"
             try: reason = response.candidates[0].finish_reason
             except: pass
             return f"-- WARNING: Gemini generation stopped ({reason})."
        except Exception as e:
            logger.error(f"An unexpected error occurred during Gemini SQL generation: {e}", exc_info=True)
            return f"-- ERROR: Unexpected error during Gemini call: {e}"
        
    def generate_sql(self, prompt: str) -> str:
        """Generates SQL using Gemini model. Returns cleaned text or error string."""
        logger.info(f"Calling Gemini model '{self.model_name}' for SQL generation.")
        # Construct prompt specific to SQL generation task
        full_prompt = f"""**Task:** Generate a syntactically correct SQL query for SQLite based on the provided schema and user question.
**Output Requirements:** ONLY output the SQL query. Do not include explanations, markdown formatting (like ```sql), or any other text.

**Schema:**
{prompt}

**SQL Query:**"""
        return self._call_gemini(full_prompt)

    def predict_tables(self, prompt: str) -> str:
        """Predicts relevant tables using Gemini model. Returns cleaned text or error string."""
        logger.info(f"Calling Gemini model '{self.model_name}' for table prediction.")
        # The prompt received here is already formatted by generate_table_prediction_prompt
        # No extra instructions needed as they are in the prompt itself.
        full_prompt = prompt
        return self._call_gemini(full_prompt)


# --- Factory Function / Registry ---
LLM_CLIENT_REGISTRY: Dict[str, Type[LLMClient]] = {
    "MockLLM": MockLLMClient,
    "GPT-4o Mini": OpenAIClient,
    "Gemini 1.5 Flash": GeminiClient,
}

def get_llm_client(llm_name: str, config: Dict | None = None) -> LLMClient:
    """Factory function to get an instance of the appropriate LLM client."""
    client_class = LLM_CLIENT_REGISTRY.get(llm_name)
    if not client_class:
        logger.warning(f"LLM client for '{llm_name}' not found in registry. Falling back to MockLLMClient.")
        client_class = MockLLMClient # Fallback to mock client

    try:
        # Pass any specific config needed for initialization
        # You might load API keys or model details here based on llm_name
        client_instance = client_class(config=config)
        return client_instance
    except Exception as e:
        logger.error(f"Failed to instantiate LLM client '{llm_name}': {e}", exc_info=True)
        # Optionally fallback to mock or raise an error
        logger.warning("Falling back to MockLLMClient due to instantiation error.")
        return MockLLMClient(config=config)


# --- 4. Update the LangGraph Node ---
def call_llm_node(state: GraphState) -> GraphState:
    """
    LangGraph node that uses the factory to get an LLM client
    and calls its generate_sql method.
    """
    logger.debug(f"Entering call_llm_node. Current state keys: {list(state.keys())}")
    prompt = state.get('final_prompt')
    selected_llm_name = state.get('llm_config') # Name from Streamlit/state

    if not prompt:
        logger.error("No prompt found in state for LLM call.")
        return {"generated_sql": None, "error": "Prompt generation failed."}
    if not selected_llm_name:
        logger.error("No LLM specified in state ('llm_config').")
        return {"generated_sql": None, "error": "LLM configuration missing."}

    try:
        # Get the appropriate client instance using the factory
        # Pass any necessary config (e.g., model specifics for OpenAI/HF) if needed
        # config_for_llm = {"model": "gpt-4-turbo"} # Example config passing
        llm_client = get_llm_client(selected_llm_name) # Add config if needed

        logger.info(f"Using {llm_client.__class__.__name__} for LLM call.")

        # Call the common method defined by the protocol
        generated_sql = llm_client.generate_sql(prompt)

        logger.info(f"LLM Client {llm_client.__class__.__name__} generated SQL.")
        return {"generated_sql": generated_sql, "error": None} # Success

    except Exception as e:
        # Catch errors during client instantiation or generation
        logger.error(f"Error during LLM node execution ({selected_llm_name}): {e}", exc_info=True)
        return {"generated_sql": None, "error": f"LLM Node Error: {e}"}