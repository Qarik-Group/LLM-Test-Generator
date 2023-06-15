from package import Package
from code_file import CodeFile
from langugageLookup import language_data
from pathlib import Path
from method import Method
import json


def fill_out_prompts(packages: list[Package], ext: str) -> dict:
    prompts = {}
    for package in packages:
        for file, code_file in package.source_code.items():
            prompts[file] = []
            for method in code_file.methods:
                if 'static' in method.signature or 'private' in method.signature or method.is_constructor:
                    continue
                template_values = gather_template_values(
                    ext, package, code_file, method,)
                prompt = populate_template(template_values)
                prompts[file].append(prompt)
    print(f'Prepped {len(prompts)} prompts')
    return prompts


def gather_template_values(language: str, package: Package, code_file: CodeFile, method: Method) -> dict:
    template_data = {}
    template_data['language'] = language
    template_data['testing_framework'] = language_data[language]["testing_frameworks"][0]['name']
    template_data['testing_framework_generic_import'] = language_data[language]["testing_frameworks"][0]['generic_import']

    template_data['logging_framework'] = language_data[language]["logging"][0]

    template_data['static_code_analysis'] = code_file.static_code_analysis
    template_data['source_code'] = str(method)
    reference_code = []

    template_data['reference_package_info'] = []

    for source_code in package.source_code.values():
        reference_methods = source_code.methods.copy()
        populate_reference_class_signature(
            template_data, source_code.class_signatures)
        for method in reference_methods:
            reference_code.append(
                f'{method.signature} belongs to {method.parent_class["signature"]}')
    template_data['source_code_implements'] = ''
    template_data['source_code_extends'] = ''
    template_data['source_code_fields'] = code_file.fields
    if 'implements' in code_file.class_signatures[0]:
        template_data['source_code_implements'] = code_file.class_signatures[0]['implements']
    if 'extends' in code_file.class_signatures[0]:
        template_data['source_code_extends'] = code_file.class_signatures[0]['extends']

    template_data['reference_methods'] = str(reference_code)
    template_data['code_imports'] = code_file.imports
    template_data['notes'] = ''
    template_data['class_comments'] = code_file.class_comments
    template_data['package'] = package.package_path
    template_data['method_comments'] = [method.comment]
    return template_data


def populate_reference_class_signature(template_data: dict, class_signatures: list[dict]):
    reference_sig = ''
    for value in class_signatures:
        reference_sig += f'{value["name"]} -- type: {value["type"]}'
        if 'extends' in value:
            reference_sig += " extends: " + ', '.join(value["extends"])
        if 'implements' in value:
            reference_sig += " implements: " + ', '.join(value["implements"])

        reference_sig += ','

    template_data['reference_package_info'].append(reference_sig)


def populate_template(template_data: dict) -> dict:
    with open("template_prompts/methodprompt.json", "r") as file:
        data = json.load(file)
        context = ''
        for item in data["context"]:
            title = str(item).replace('_', ' ')
            context += f'{title}: {data["context"][item].format(**template_data)} \n'
        question = data["question"].format(**template_data)
        context = context.replace('static code analysis: []', '')
        context = context.replace('method comments: ['']', '')

        return {'question': question, 'context': context}

# Provide the values for the placeholders
# values = {
#     'programming_language': 'Python',
#     'testing_framework_tool': 'pytest',
#     'source_code': '[Provide the relevant source code here]',
#     'static_code_analysis_results': '[Include the static code analysis results here]',
# }

# # Render the template with the values
# result = template.format(**values)
    pass


"My name is {name} and I am {age} years old."
"""I need you to generate unit tests for a piece of source code written in {programming_language}. Your goal is to create high-quality unit tests that achieve the best line coverage possible while focusing on simplicity and clarity.
Consider the following guidelines when generating the tests:

- Use {{ testing_framework_tool }} for writing the unit tests.
- Include the package name.
- Use only provided methods, and do not assume there are public getters and setters unless found in the source code.
- Leverage static code analysis results to identify dependencies and libraries used by the source code.
- Focus on testing one function at a time and utilize mocks where possible.
- Include checks for boundary conditions without redundancy.
- Test error handling where applicable, but ensure the tests do not fail if the source code lacks specific exception or null pointer handling.
- Prioritize achieving line coverage without unnecessary complexity.
- Performance or resource-related aspects do not need to be addressed.
- Test descriptions should be concise, but you may add a small comment to describe complex sections if needed.

Please generate a set of unit tests that thoroughly test the source code, aiming to achieve the best line coverage possible. You can assume that the input source code may vary in size, and the organization or structure of the unit tests will be determined by the language and style used. Avoid redundant tests and prioritize simplicity in the test scenarios.

Context:
{{ source_code }}

Static Code Analysis Results:
{{ static_code_analysis_results }}

Please generate the unit tests for {{ src_file_name }} accordingly.

"""
