import os
from google.genai import types
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory: str, directory = ".") -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir,directory))
        valid_target_dir = os.path.commonpath([abs_working_dir, target_dir]) == abs_working_dir
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

    except Exception as e:
        return f"Error: {e}"

    # return f'Success: "{directory}" is within the working directory'
    try:
        result = "\n".join(map(lambda x: format_file_info(target_dir, x),os.listdir(target_dir)))
    except Exception as e:
        return f"Error: {e}"
    return result

def format_file_info(target_dir, name):
    path = os.path.join(target_dir, name)
    file_info = f"- {name}: file_size={os.path.getsize(path)} bytes, is_dir={os.path.isdir(path)}"
    return file_info

