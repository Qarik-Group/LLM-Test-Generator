from method import Method
from pathlib import Path


class CodeFile:
    def __init__(self, class_signatures: dict, class_comments: list[str], fields: list[str], methods: list[Method], path: Path, package: str, imports: list[str], static_code_analysis: list[str]) -> None:
        self.class_signatures = class_signatures
        self.class_comments = class_comments
        self.fields = fields
        self.methods = methods
        self.path = path
        self.package = package
        self.imports = imports
        self.static_code_analysis = static_code_analysis

    def test_name(self) -> str:
        return self.path.with_stem(self.path.stem + "Test").name
