import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs the file using subprocess and passes the args needed for the file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to be runned by subprocess,it will run if its a file, and its in the working dir"),
            "args": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.STRING,
            ),
            description="A list of strings containing the args passed to the run_python_file function,")
        },required=["file_path"]
    ),
)

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        if ".py" not in file_path:
            return f'Error: "{file_path}" is not a Python file' 
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir,file_path))
        valid_target_dir = os.path.commonpath([abs_working_dir, target_dir]) == abs_working_dir
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_dir):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        command = ["python", target_dir]
        if args:
            command.extend(args)
        completed = subprocess.run(command,cwd=abs_working_dir,capture_output=True,text=True,timeout=30)
        result = ""
        if completed.returncode != 0:
            result += f"Process exited with code {completed.returncode}\n"
#        print(f"TEST STDOUT: {completed.stdout} STR CHECK: {completed.stdout == ""}\nTEST STDERR: {completed.stderr} STR CHECK: {completed.stderr == ""}")
        if not len(completed.stdout) and not len(completed.stderr):
            result += "No output produced"
        else:
            result += f"STDOUT:{completed.stdout}\nSTDERR:{completed.stderr}"
        return result

    except Exception as e:
        return f"Error: {e}"
