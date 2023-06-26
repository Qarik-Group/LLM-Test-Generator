from pathlib import Path


def postprocess(results: dict):
    """Process the results from the LLM. Clean up text, save to file

    Args:
        results (dict): the results from the LLM
    """
    for path, result in results.items():
        content = remove_excess_text(result)
        content = rename_test(path.stem, content)

        try:
            save(path, content)
        except Exception as e:
            print(f'Failed saving file: {e}')
            continue


def save(path: str, content: str):
    """Save the contents to the test directory of the respective module

    Args:
        path (str): path of the new test
        content (str): content to save
    """
    print(f'Writing tests to {str(path)}')
    pass
    with open(path, 'w') as file:
        file.write(content)


def rename_test(name: str, content: str) -> str:
    """Rename the test class to the file name

    Args:
        name (str): name to use
        content (str): content of the new test file

    Returns:
        str: edited content
    """
    class_name_start = content.index("class") + len("class")
    class_name_end = content.index("{", class_name_start)

    content = content[:class_name_start] + \
        ' '+name + content[class_name_end:]
    return content


def remove_excess_text(content: str) -> str:
    """Remove non-code responses, and code section indicators

    Args:
        content (str): test file content

    Returns:
        str: cleaned up text
    """
    llm_comments_start = content.index("```java") + len("```java")
    content = content[llm_comments_start:]
    content = content.replace('```', '')
    return content
