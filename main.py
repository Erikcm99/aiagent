import os
from prompts import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse
from functions.call_function import available_functions
import argparse

def get_token_usage(response: GenerateContentResponse):
    if response.usage_metadata is None:
        raise RuntimeError("Failed to print response metadata, check for a api request fail")
    metadata = response.usage_metadata
    return f"Prompt tokens: {metadata.prompt_token_count}\nResponse tokens: {metadata.candidates_token_count}"

def check_api():
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key is None:
        raise RuntimeError("The api key was not found")
    return api_key


def main():
    load_dotenv()
    api_key = check_api()
    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="AiAgent")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    generated_content: GenerateContentResponse = client.models.generate_content(
        model="gemini-2.5-flash", contents=messages,config=types.GenerateContentConfig(tools=[available_functions],system_instruction=system_prompt))

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(get_token_usage(generated_content))
              
    if generated_content.function_calls:
        for function_call in generated_content.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(generated_content.text)

if __name__ == "__main__":
    main()
