# LLM-Test-Generator
Proof of concept: Can a Large Language Model Generate Unit tests

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
