from package import Package
from langugageLookup import language_data
from langugageLookup import llm_data


def fill_out_prompts(packages: list[Package], ext: str):

    for package in packages:
        for filepath in package.source_code.keys():
            template_values = gather_template_values(ext, package, filepath)

            populate_template(filepath, package, template_values)

        pass


def gather_template_values(language: str, package: Package, filepath: str) -> dict:
    template_data = {}
    template_data["language"] = language
    template_data["testing_framework"] = language_data[language]["testing_frameworks"][0]
    template_data["source_code"] = package.source_code[filepath]
    return template_data


def populate_template(filepath: str, package: Package, template_data: dict) -> str:
    with open("template_prompts/singleprompt.txt", "r") as file:

        template = file.read()
        template = template.format(programming_language=template_data["language"], testing_framework_tool=template_data[
                                   "testing_framework"], source_code="", static_code_analysis_results="", src_file_name="")
        # print(template)

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
