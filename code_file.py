# Copyright 2023 Qarik Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from method import Method
from pathlib import Path


class CodeFile:
    def __init__(self, class_signatures: list[dict], class_comments: list[str], fields: list[str], methods: list[Method], path: Path, package: str, imports: list[str], static_code_analysis: list[str]) -> None:
        self.class_signatures = class_signatures
        self.class_comments = class_comments
        self.fields = fields
        self.methods = methods
        self.path = path
        self.package = package
        self.imports = imports
        self.static_code_analysis = static_code_analysis
