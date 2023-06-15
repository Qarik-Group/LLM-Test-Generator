from sonarqube import SonarQubeClient
import subprocess
import time
from pathlib import Path
import json


def analyze(directory: Path):
    start_sonarqube()
    project = directory.parts[-1]
    sonar = SonarQubeClient(sonarqube_url="http://localhost:9000",
                            username='admin', password='admin1')
    projects = sonar.projects.search_projects(
        projects=[project])
    found = any(component['key'] ==
                project for component in projects['components'])

    run_analysis(found, str(directory.absolute()))
    results = retrieve_results(sonar, project)
    parsed_results = parse_results(results, directory)

    shutdown_sonarqube()
    return parsed_results


def parse_results(results: dict, directory: Path) -> dict:
    parsed_results = {}
    # with open("data.json", "w") as json_file:
    #     json.dump(results, json_file)
    for issue in results['issues']:
        if not (".java" in issue['component']):
            continue
        relative_path = issue['component'].split(':')[1]
        absolute_path = str(directory.absolute().joinpath(relative_path))
        if absolute_path not in parsed_results:
            parsed_results[absolute_path] = []
        parsed_results[absolute_path].append(issue['message'])
    return parsed_results


def shutdown_sonarqube():
    print('---\tStopping Sonarqube Server\t---')
    # subprocess.Popen(
    #     ["/Users/sonarqube-10.0.0.68432/bin/macosx-universal-64/sonar.sh", "stop"], stdout=subprocess.DEVNULL)


def run_analysis(cached: bool, path: str):
    if cached:
        print('Project has been previously analyzed. Skipping analysis')
        return
    print('---\tStatic Code Analysis Starting\t---')

    subprocess.run(
        ["/Users/jake/Applications/apache-maven-3.9.2 2/bin/mvn",
         "sonar:sonar",
         "-Dsonar.host.url=http://localhost:9000",
         "-Dsonar.login=admin",
         "-Dsonar.password=admin1"],
        cwd=path,
        stdout=subprocess.DEVNULL)
    print('---\tStatic Code Analysis Finished\t---')


def retrieve_results(sonar: SonarQubeClient, project: str):
    print('---\tQuerying for Results\t---')
    return sonar.issues.search_issues(componentKeys=project, branch="main")


def start_sonarqube():
    print('---\tSonarqube Server Starting\t---')
    # subprocess.Popen(
    #     ["/Users/sonarqube-10.0.0.68432/bin/macosx-universal-64/sonar.sh", "console"], stdout=subprocess.DEVNULL)
    # # Sleeps until the server has started.
    # time.sleep(40)
    print('---\tSonarqube Server Started\t---')
