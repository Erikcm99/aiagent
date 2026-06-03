import os
from prompts import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse
from functions.call_function import available_functions, call_function
import argparse
import sys

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
    for _ in range(20):
        generated_content: GenerateContentResponse = client.models.generate_content(
            model="gemini-2.5-flash", contents=messages,config=types.GenerateContentConfig(tools=[available_functions],system_instruction=system_prompt))
        if generated_content.candidates:
            for content in generated_content.candidates:
                messages.append(content.content)
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(get_token_usage(generated_content))
        if generated_content.function_calls:
            function_results = []
            for function_call in generated_content.function_calls:
                function_call_result = call_function(function_call)
                if not function_call_result.parts:
                    raise Exception("Parts in function call not found")
                function_parts = function_call_result.parts[0]
                if function_parts.function_response == None:
                    raise Exception("Parts list present, but first item is None")
                function_results.append(function_parts)
                messages.append(types.Content(role="user", parts=function_results))
                if args.verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
        else:
            print(generated_content.text)
            return
    print("Reached the limit of AI request at 20 iterations, exiting")
    sys.exit(1)

if __name__ == "__main__":
    main()
