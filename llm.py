from vertexai.preview.language_models import ChatModel, InputOutputTextPair
import json


def generate_tests(prompts: dict) -> None:

    chat_model = ChatModel.from_pretrained("chat-bison@001")

    # TODO developer - override these parameters as needed:
    parameters = {
        # Temperature controls the degree of randomness in token selection.
        "temperature": .2,
        # Token limit determines the maximum amount of text output.
        "max_output_tokens": 1024,
        # Tokens are selected from most probable to least until the sum of their probabilities equals the top_p value.
        "top_p": 0.95,
        # A top_k of 1 means the selected token is the most probable among all tokens.
        "top_k": 40,
    }

    prompt_list = prompts['/Users/jake/Projects/java-design-patterns/ambassador/src/main/java/com/iluwatar/ambassador/RemoteService.java']
    print(prompt_list[0]['context'])
    with open('final_prompt.json', 'w') as file:
        json.dump(prompt_list[0], file)

    chat = chat_model.start_chat(
        context=prompt_list[0]['context']
    )
    response = chat.send_message(
        prompt_list[0]['question'], **parameters)
    # response = chat.send_message(
    #     'You just generated code that tries to instantiate an interface. How can I improve my prompt to indicate that I want that made into an annonymous function, or use an implementation inside the same package?', **parameters)
    with open('output.java', 'w') as file:
        file.write(response.text)
    # print('\n--------------\n')

    # for file, prompt_list in prompts.items():
    #     print(file)
    #     for prompt in prompt_list:
    #         chat = chat_model.start_chat(
    #             context=prompt['context'],

    #         )

    #         response = chat.send_message(prompt['question'], **parameters)
    #         print(f"{response.text}")
    # exit()
