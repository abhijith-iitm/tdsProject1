from fastapi import FastAPI, Query, HTTPException
import google.generativeai as genai
import os
import time

MAX_RETRIES = 20  # Max number of retries before giving up
TIME_LIMIT = 100  # Time limit in seconds for the retry process

app = FastAPI()

# Set your Gemini API key (replace with environment variable for security)
GEMINI_API_KEY = "AIzaSyDp0f_0tGRqabaJc8oeea8_37hrMLHq7Ok"  
# Replace this with your actual key
genai.configure(api_key=GEMINI_API_KEY)

def generate_python_script(task: str) -> str:
    """
    Uses Google's Gemini AI to generate a Python script for the requested task.
    Ensures only valid Python code is returned.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Write a Python script to perform the following task: {task}."
                                          "Make sure to handle multiple input formats (for dates, etc)."
                                          "Make sure to iterate recursively in case of nested directories.")

        script = response.text.strip()

        # Ensure the response contains only Python code
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
    try:
        exec(script, {}, local_vars)  # Execute in a restricted environment
        return local_vars.get("result", "Execution successful, but no result returned.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

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
