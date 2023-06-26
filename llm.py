from vertexai.preview.language_models import ChatModel, InputOutputTextPair
import json
from pathlib import Path


def generate_tests(prompts: dict) -> dict:

    chat_model = ChatModel.from_pretrained("chat-bison@001")

    parameters = {
        # Temperature controls the degree of randomness in token selection.
        "temperature": .8,
        # Token limit determines the maximum amount of text output.
        "max_output_tokens": 1024,
        # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
        "top_p": 0.4,
        # A top_k of 1 means the selected token is the most probable among all tokens.
        "top_k": 15,
    }
    final_results = {}
    for path, prompt_list in prompts.items():
        results = []
        name = f'{Path(path).stem}GenTest'
        name = name.replace('.', '_')
        print(f'Generating tests for {str(path)}')
        for prompt in prompt_list:

            context = json.loads(prompt['context'])
            chat = chat_model.start_chat(
                context=json.dumps(context)
            )
            response = ''
            try:
                response = chat.send_message(
                    prompt['question'], **parameters)
            except Exception as e:
                print(f'Error when connecting to the LLM: {e}')
                continue

            results.append(response.text)
        print(f'Generated test(s) for {str(path)}')

        res = ''
        path = path.replace('main', 'test')
        path = Path(path)
        test_path = path.with_name(name).with_suffix('.java')

        if len(results) > 1:
            try:
                res = combine_tests(chat_model, results, parameters)
            except Exception as e:
                print(f'Failed combining tests: {e}')
                continue

            final_results[test_path] = res
        elif results:

            res = results[0]
            final_results[test_path] = results[0]

    return final_results


def combine_tests(chat_model, results: list[str], parameters: dict):
    chat = chat_model.start_chat(
        context=", ".join(results)
    )
    return chat.send_message(
        f'Combine the following tests into one java test file. Add in any imports for core java code lists, queues, maps, etc that are missing', **parameters).text
