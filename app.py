from fastapi import FastAPI, Query, HTTPException
import google.generativeai as genai
import os
import time
from googletrans import Translator
import sys
import re
import io

MAX_RETRIES = 20  # Max number of retries before giving up
TIME_LIMIT = 100  # Time limit in seconds for the retry process
SAFE_LIBRARIES = ["os", "datetime", "math", "json", "re", "csv", "pandas", "time", "PIL"]  # Allowed imports


app = FastAPI()

# Set your Gemini API key (replace with environment variable for security)
GEMINI_API_KEY = "AIzaSyDp0f_0tGRqabaJc8oeea8_37hrMLHq7Ok"  
# Replace this with your actual key
genai.configure(api_key=GEMINI_API_KEY)

def detect_and_translate(task: str) -> str:
    """
    Detects the language of the task and translates it to English if necessary.
    """
    translator = Translator()
    detected_lang = translator.detect(task).lang  # Detect the task language

    if detected_lang != "en":  # If task is not in English, translate it
        task = translator.translate(task, src=detected_lang, dest="en").text
        print(f"Translated Task ({detected_lang} → en): {task}")

    return task

def generate_python_script(task: str) -> str:
    """
    Uses Google's Gemini AI to generate a Python script for the requested task.
    Ensures only valid Python code is returned.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        
        # Translate task if it's not in English
        task = detect_and_translate(task)

        prompt = f"""
        You are an advanced AI-powered Python assistant. Your job is to generate a **fully functional Python script** 
        that correctly performs the task given below.

        **Requirements:**
        - **DO NOT** include explanations or markdown formatting.
        - **Ensure the script is structured, optimized, and directly executable.**
        - **Use appropriate libraries** depending on the task (e.g., `os`, `json`, `math`, `requests`, `pandas`, `datetime`).
        - **If the task involves API calls, generate a script that fetches data via `requests`.**
        - **If the task involves data analysis, use `pandas` or `numpy`.**
        - **If the task is mathematical, use `math` or `sympy`.**
        - **Ensure all operations have proper error handling.**
        - **Ensure all file paths are relative to the `./data/` directory.**
        - **DO NOT execute any system-modifying commands (e.g., deleting files, changing system settings).**
        - **The script must handle multiple date formats:**
          - `YYYY-MM-DD`
          - `DD-MM-YYYY`
          - `MM-DD-YYYY`
          - `YYYY-DD-MM`
          - `"Dec 29, 2008"` (Month abbreviation format)
          - `"2019/11/15 01:57:05"` (Timestamps with time)
          - `"09-Oct-2014"` (Day-Month-Abbreviation-Year format)
        - **If the file is missing or empty, return a meaningful error message.**
        - **Use `datetime` for date parsing and checking if a date is a Wednesday.**
        - **Iterate safely through the file and handle missing or invalid date entries.**

        Task: "{task}"
        """

        response = model.generate_content(prompt)
        script = response.text.strip()

        # Ensure only valid Python code is returned
        if "```python" in script:
            script = script.split("```python")[1].split("```")[0].strip()

        return script
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
    
def execute_python_script(script: str) -> str:
    """
    Executes the generated Python script safely and captures its output.
    """
    local_vars = {}

    print("Generated Python script:\n", script)

    # Validate that the script only imports safe libraries
    unsafe_imports = re.findall(r"import\s+([a-zA-Z0-9_]+)", script)
    for lib in unsafe_imports:
        if lib not in SAFE_LIBRARIES:
            raise HTTPException(status_code=400, detail=f"Unsafe library used: {lib}")

    # Redirect stdout to capture print output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        exec(script, {}, local_vars)  # Execute safely
        output = sys.stdout.getvalue().strip()  # Capture output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")
    finally:
        sys.stdout = old_stdout  # Restore stdout

    return output if output else "Execution successful, but no result returned."

def run_with_retry(task: str, max_retries: int = MAX_RETRIES, time_limit: int = TIME_LIMIT) -> dict:
    """
    Tries to generate and execute the Python script within a max number of retries and time limit.
    """
    start_time = time.time()
    attempt = 0
    
    while attempt < max_retries and (time.time() - start_time) < time_limit:
        try:
            # Step 1: Generate Python script using Gemini LLM
            script = generate_python_script(task)
            print(f"Attempt {attempt + 1}: Generated script")

            # Step 2: Try executing the script
            result = execute_python_script(script)
            
            # If execution is successful, return the result
            return {"status": "success", "script": script, "output": result}

        except HTTPException as e:
            # If a known HTTPException occurs, raise it immediately
            raise e
        except Exception as e:
            # If there's an error (script generation or execution), retry
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            attempt += 1
            time.sleep(2)  # Wait for a moment before retrying
            
    # If all attempts fail, return a failure response
    raise HTTPException(status_code=500, detail="Max retries reached or time limit exceeded while generating/executing script.")

@app.post("/run")
async def run_task(task: str = Query(..., description="Task description to execute")):
    """
    Parses a natural language task, generates Python code, executes it, and returns the result.
    Includes retry logic to keep trying until execution succeeds or the retry limit/time is reached.
    """
    try:
        result = run_with_retry(task)  # Call the retry logic

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
    
@app.get("/read")
async def read_file(path: str = Query(..., description="File path to read")):
    """
    Reads the content of a specified file.
    Returns:
        - 200 OK with file content
        - 404 Not Found if file does not exist
    """
    if not os.path.isfile(path):
        print(f"Current working directory: {os.getcwd()}")
        print("Os Path", os.path)
        print(path)
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
