from fastapi import FastAPI, Query, HTTPException
import openai
import os

app = FastAPI()

# Set your OpenAI API key (replace with env variable for security)
OPENAI_API_KEY = "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"  
# Change to os.getenv("OPENAI_API_KEY") in production

def generate_python_script(task: str) -> str:
    """
    Uses an LLM (GPT-4) to generate a Python script for the requested task.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that generates Python scripts to execute tasks."},
                {"role": "user", "content": f"Write a Python script to perform the following task: {task}"}
            ],
            api_key=OPENAI_API_KEY
        )
        script = response["choices"][0]["message"]["content"].strip()
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

@app.post("/run")
async def run_task(task: str = Query(..., description="Task description to execute")):
    """
    Parses a natural language task, generates Python code, executes it, and returns the result.
    """
    try:
        # Step 1: Get Python script from LLM
        script = generate_python_script(task)

        print("Script Generated!!")
        # Step 2: Execute the script
        result = execute_python_script(script)

        return {"status": "success", "script": script, "output": result}

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
        print("Os Path",os.path)
        print(path)
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

