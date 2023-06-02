import pathlib
from static_analysis_data import StaticAnalysisData


class Package:
    def __init__(self, package_path: pathlib.Path, source_code: dict, static_analysis_data: StaticAnalysisData, test_code: dict):
        self.package_path = package_path
        self.static_analysis_data = static_analysis_data
        self.source_code = source_code
        self.test_code = test_code

    @property
    def test_path(self) -> pathlib.Path:
        return self.package_path.joinpath("tests")

    @property
    def src_path(self) -> pathlib.Path:
        return self.package_path.joinpath("main")

    def src_tokens(self) -> int:
        tokens = 0
        for src in self.source_code.keys():
            tokens += int(len(self.source_code[str(src)].split())/.75)
        return tokens

    def test_tokens(self) -> int:
        tokens = 0
        for test in self.test_code.keys():
            tokens += int(len(self.test_code[str(test)].split())/.75)
        return tokens

    def validation_tokens(self) -> int:
        tokens = 0
        for src in self.source_code.keys():
            if str(src) in self.static_analysis_data:
                for violation in self.static_analysis_data[str(src)].violations:
                    tokens += int(len(violation)/.75)
        for test in self.test_code.keys():
            if str(test) in self.static_analysis_data:
                for violation in self.static_analysis_data[str(test)].violations:
                    tokens += int(len(violation)/.75)
        return tokens

    def total_tokens(self) -> int:
        return self.src_tokens()+self.test_tokens()+self.validation_tokens()

    def get_full_context(self) -> str:
        context = ""
        for file in self.source_code:
            context += self.source_code[file]
        return context

    def __str__(self):
        temp_result = ""

        result = f"{self.package_path.parent.name}"

        return result
