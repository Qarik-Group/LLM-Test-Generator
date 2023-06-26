# LLM-Test-Generator
Proof of concept: Can a Large Language Model Generate Unit tests

## Setup
You need to be signed into the gcloud cli tool.
- Run `gcloud auth login`
And you need to be using a project with vertex AI enabled

## Running

To run this - Use `python3 testgenerator <path_to_java_project> java`

At this time you will have to go into `static_code_analysis.py` and update the absolute path to `mvn`, since I can't get python to locate it (I will look into this more later). Change `/Users/jake/Applications/apache-maven-3.9.2 2/bin/mvn"` to wherever your mvn bin is located
