from code_file import CodeFile
import os
from method import Method
from package import Package
from pathlib import Path
import re
from static_analysis_data import StaticAnalysisData
from static_code_analysis import analyze


def preprocess(directory: Path, ext: str) -> list[Package]:
    """Preprocesses the entire repository by creating Package objects with the parsed data from all of the files

    Args:
        directory (Path): Path to the root of the repository that is being preprocessed
        ext (str): Extension of the language being parsed (6/1/2023 - Only supports Java)

    Returns:
        list[Package]: All the parsed packages from the repository
    """
    packages = []
    package_dirs: list[Path] = find_packages(directory)
    analysis_data = analyze(directory)
    i = 0
    for package_dir in package_dirs:

        source_file_paths = find_files(package_dir, "main", ext)
        test_file_paths = find_files(package_dir, "test", ext)
        source_files = {}
        test_files = {}

        for file in source_file_paths:
            file_static_analysis = []

            if str(file.absolute()) in analysis_data:
                file_static_analysis = analysis_data[str(file.absolute())]
            code: CodeFile = parse_file(file, file_static_analysis)
            if code is None:
                continue
            source_files[str(file.absolute())] = code
        # for file in test_file_paths:
        #     code: CodeFile = parse_file(file)
        #     if code is None:
        #         continue
        #     test_files[str(file.absolute())] = code
        package = parse_package_value(source_file_paths[0])

        packages.append(Package(package, package_dir, source_files,
                        analysis_data, test_files))
    return packages


def parse_package_value(path: Path) -> str:
    package_parts = []
    path, _ = os.path.split(path)
    while True:
        path, folder = os.path.split(path)
        if folder == 'java' or folder == 'src':
            break
        package_parts.append(folder)
        if not path:
            break
    package_parts.reverse()
    package_name = '.'.join(package_parts)

    return str(package_name)


def parse_file(file: Path, static_code_analysis: list[dict]) -> CodeFile:
    """Parses a java file for useful context information, including package, imports, class comments, and methods

    Args:
        file (Path): Path of the java file

    Returns:
        CodeFile: CodeFile object with relevant parsed data, may be None if there are no methods present
    """
    with open(file, "r") as input_file:
        java_code = input_file.read()
        package = parse_package(java_code)
        class_signatures = parse_class(java_code)
        class_signatures = get_signature_info(class_signatures)

        imports = parse_imports(java_code)
        class_comments = parse_class_comments(java_code.splitlines())
        fields = parse_class_fields(java_code)
        methods = parse_methods(java_code, class_signatures)
        if len(methods) == 0:
            return None
        return CodeFile(class_signatures, class_comments, fields, methods, file, package, imports, static_code_analysis)


def parse_class_fields(code: str) -> list[str]:
    field_pattern = (
        # Access modifiers
        r'((?:public\s*|protected\s*|private\s*)*'
        # modifiers
        r'(?:abstract\s*|synchronized\s*|static\s*|final\s*|transient\s*|volatile\s*)*'
        # Return type
        r'(?:void|[A-Za-z0-9<>\[\]]+) '
        # Variable name
        r'(?:[A-Za-z0-9_]+)'
        # Optional assignment value
        r'(?:\s*=\s*[A-Za-z0-9" \.]*)*;)'
    )
    matches = re.findall(field_pattern, code)
    fields = []
    for field in matches:
        fields.append(field)
    return fields


def get_signature_info(class_signatures: list[str]) -> list[str]:
    signatures = []
    for signature in class_signatures:
        typ = ('class'if 'class' in signature else
               'enum' if 'enum' in signature else 'interface')
        extends_pattern = r'extends\s*([A-Za-z0-9<>]*)\s*'
        implements_pattern = r'implements\s*([A-Za-z0-9<>]*)\s*'
        name_pattern = (
            # Name
            r'((?:[A-Za-z0-9<>]*))\s*'
            # Helps extract only the name
            r'(?:extends\s*[A-Za-z0-9<>]*)*\s*'
            # Helps extract only the name
            r'(?:implements\s*[A-Za-z0-9<>]*)*\s*\{')
        extends_matches = re.findall(extends_pattern, signature)
        implements_matches = re.findall(implements_pattern, signature)
        name_matches = re.findall(name_pattern, signature)
        signatureInfo = {'signature': signature, 'type': typ}
        if extends_matches:
            signatureInfo['extends'] = extends_matches
        if implements_matches:
            signatureInfo['implements'] = implements_matches
        if name_matches:
            signatureInfo['name'] = name_matches[0]
        signatures.append(signatureInfo)
    return signatures


def parse_class(code: str) -> list[str]:
    """Retrieves the package string at the beginning of the file

    Args:
        code (str): the full text of a java code document

    Returns:
        str: The package declaration, may be empty string
    """
    class_pattern = (
        # Access modifers
        r"((?:public\s*|protected\s*|private\s*)*"
        # class keywork and name
        r"(?:class|enum|interface)\s*(?:[A-Za-z0-9<>]*)\s*"
        # optional extends and name
        r"(?:extends\s*[A-Za-z0-9<>]*)*\s*"
        # optional implements and name
        r"(?:implements\s*[A-Za-z0-9<>]*)*\s*\{)")
    matches = re.findall(class_pattern, code)
    classes = []
    for cls in matches:
        classes.append(cls)
    return classes


def parse_package(code: str) -> str:
    """Retrieves the package string at the beginning of the file

    Args:
        code (str): the full text of a java code document

    Returns:
        str: The package declaration, may be empty string
    """
    package_pattern = r"(package\s+.*;)"
    match = re.findall(package_pattern, code)
    if match:
        return match[0]
    return ""


def parse_imports(code: str) -> list[str]:
    """Retrieves all the imports in a in a file

    Args:
        code (str): the full text of a java code document

    Returns:
        list[str]: All of the imports found, may be empty
    """
    imports = []
    import_pattern = r"(import\s+.*;)"
    matches = re.findall(import_pattern, code)
    for imp in matches:
        imports.append(imp)
    return imports


def parse_methods(code: str, class_signatures: list[str]) -> list[Method]:
    """Retrieves all the methods in a file, parsing by method comments, method signatures, and method body

    Args:
        code (str): the full text of a java code document

    Returns:
        list[Method]: A list of Methods found in the file, may be empty
    """
    methods = []
    method_signature_pattern = (
        # don't match keywords
        r"\b(?!\s*if|\s*new|\s*else|\s*while|\s*catch|\s*return|\s*switch|\s*synchronized\b)"
        # match access modifiers
        r"((?:public\s*|protected\s*)*"
        # match modifiers
        r"(?:static\s*|final\s*|native\s*|synchronized\s*|abstract\s*|default\s*|transient\s*)*"
        # match return type
        r"(?:void\s|[A-Za-z0-9<>\[\]\?, \.]+\s*)"
        # match method name
        r"(?:\w+\s*)"
        # match method parameters
        r"(?:\([A-Za-z0-9 ,<>\?]*\))"
        # match exception throws
        r"(?: throws \w+|))"
        # match curly brackets and new lines
        r"(?:\s*{)(?:\n*\s*)")

    matches = re.findall(method_signature_pattern, code)
    for signature in matches:
        if 'private' in signature:
            continue

        body = get_next_method(code, code.index(signature)+len(signature)+1)
        if body == "":
            continue
        parent_class = get_parent_class(
            code, code.index(signature)-1, class_signatures)
        method_comment = get_comment_before(code, code.index(signature)-1)

        constructor = is_constructor(signature)
        methods.append(Method(signature, body, method_comment,
                       parent_class, constructor))

    return methods


def is_constructor(signature: str) -> bool:
    constructor_pattern = r"^\s*((?:public\s*|protected\s*|)(?:[A-Za-z0-9<>])+\s*(?:\([A-Za-z0-9 ,<>\?]*\)))"
    matches = re.findall(constructor_pattern, signature)
    if matches:
        return True
    return False


def get_parent_class(code: str, index: int, class_signatures: list[str]) -> str:
    if len(class_signatures) == 1:
        return class_signatures[0]
    for i in range(index, -1, -1):
        if code[i:i+5] == 'class':
            for signature in class_signatures:
                lower = (i-10 if i-10 >= 0 else 0)
                upper = (i+200 if i+200 < len(code) else len(code))
                if signature['signature'] in code[lower:upper]:
                    return signature


def get_comment_before(code: str, index: int) -> str:
    """Retrieves the comment right before the method signature

    Args:
        code (str): the full text of a java document
        index (int): the index right before the start of the method signature

    Returns:
        str: either the comment before, or empty string
    """
    comment = ""
    sampling = False
    for i in range(index, -1, -1):
        if code[i] == '/' and code[i-1] == '*':
            sampling = True
        if sampling:
            comment += code[i]
        if code[i] == '*' and code[i-1] == '*' and code[i-2] == '/':
            comment += "*/"
            sampling = False
            break
        if code[i] == '*' and code[i-1] == '/':
            comment += "/"
            sampling = False
            break
        if not sampling and (code[i] == '}' or code[i] == '{'):
            break

    return comment[::-1]


def get_next_method(code: str, index: int) -> str:
    """Retrieves the next method, starting at the index given

    Args:
        code (str): the full text of a java document
        index (int): index of where to start looking for the next method

    Returns:
        str: _description_
    """
    if code[index] != "{":
        print("Expected a '{' " + f"but got '{code[index]}'")
        return
    curly_stack = []
    body = ""
    for c in code[index:]:
        if c == "{":
            curly_stack.append("{")
        elif c == "}":
            curly_stack.pop()
        body += c
        if len(curly_stack) == 0:
            break
    return body


def parse_class_comments(code: str) -> list[str]:
    """Gets the class comments, matching the '/**' for the start, and '*/' for the end

    Args:
        code (str): the full text of a java document

    Returns:
        list[str]: List of class comments, may be empty
    """
    sampling = False
    current_comment = ""
    comments = []
    for line in code:
        if "class" in line:
            break
        if "/**" in line:
            sampling = True
        if sampling:
            current_comment += line
        if "*/" in line and sampling:
            sampling = False
            comments.append(current_comment)
            current_comment = ""

    return comments


def find_files(package: Path, sub_dir: str, ext: str) -> list[Path]:
    """Finds all files in a package with a speicifc extension

    Args:
        package (Path): The path to the package we are searching in
        sub_dir (str): The sub directory of 'src' in the package
        ext (str): The extension of the files we are searching for

    Returns:
        list[Path]: The files found, may be empty
    """
    files = []
    for item in package.joinpath(sub_dir).glob('**/*'):
        if item.is_file() and "."+ext in str(item.name):
            files.append(item)
    return files


def find_packages(repository_root: Path) -> list[Path]:
    """Find the packages in the repository where 'src' is the current directory

    Args:
        repository_root (Path): Root of the project

    Returns:
        list[Path]: List of paths to each package
    """
    packages = []
    for item in repository_root.glob('**/*'):
        if item.is_dir() and "src" in str(item.name):
            packages.append(item)
    return packages
