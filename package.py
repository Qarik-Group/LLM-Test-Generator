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

import pathlib
from code_file import CodeFile


class Package:
    def __init__(self, package: str, package_path: pathlib.Path, source_code: dict[str, CodeFile], static_analysis_data: dict, test_code: dict):
        self.package = package
        self.package_path = package_path
        self.static_analysis_data = static_analysis_data
        self.source_code = source_code
        self.test_code = test_code

    def __str__(self):

        result = f"{self.package_path.parent.name}"

        return result
