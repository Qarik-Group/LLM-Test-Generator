# LLM-Test-Generator

## Goal
Testing code thoroughly requires substantial time and effort. Companies with limited resources often struggle to create high-quality tests, resulting in issues in the production environment.
This proof of concept was made to see if we can use a Large Language Model to generate unit tests for arbitrary source code.
This POC focuses on java unit tests.

:warning: Please be aware, at this point, this has produced results that are reasonably close to quality tests, but still needs manual intervention. :warning:


## Setup
Tools:
- [Maven](https://maven.apache.org/download.cgi)
- [gcloud cli](https://cloud.google.com/sdk/docs/install)
    - Google Cloud Project with Vertex AI enabled
- [SonarQube](https://www.sonarsource.com/products/sonarqube/downloads/)
    - Add the corresponding bin folder to the path (e.g - `sonarqube-10.0.0.68432/bin/macosx-universal-64/`)
    - Add credentials as environment variables `SONAR_USER` and `SONAR_PASS`

## Running

To run this - Use `python3 test_generator.py <git_url>`
Optional - use `--module=<module_path>` (relative to the target repository root) to make the generation set smaller


## Viewing Results

The generated tests can be found in the test folders of their corresponding modules in the target repository. They will be named `<Source File Name>GenTest.java`
You can find the final prompts for each of the methods in `final_prompts` once they have been prepared
You may need to make manual edits, but it is still faster than writing the tests from scratch


