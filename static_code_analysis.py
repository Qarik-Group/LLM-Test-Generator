from sonarqube import SonarQubeClient
import subprocess
from pathlib import Path


def analyze(directory: Path) -> dict:
    """Uses Sonarqube to statically analyze the codebase

    Args:
        directory (Path): path to the codebase

    Returns:
        dict: results from the analysis
    """
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
    """Parse results from issues - gets all the messages

    Args:
        results (dict): the querying results
        directory (Path): path to the repository

    Returns:
        dict: parsed results
    """
    parsed_results = {}

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
    """Asyncronously shuts down sonarqube
    """
    print('---\tStopping Sonarqube Server\t---')
    # subprocess.Popen(
    #     ["/Users/sonarqube-10.0.0.68432/bin/macosx-universal-64/sonar.sh", "stop"], stdout=subprocess.DEVNULL)


def run_analysis(cached: bool, path: str):
    """Runs the analysis of the codebase

    Args:
        cached (bool): If the repository has already been analyzed, dont do it again
        path (str): Path to the repository
    """
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
    """Queries the Sonarqube server for static code analysis results

    Args:
        sonar (SonarQubeClient): The sonarqube client object to query
        project (str): the project we are querying

    Returns:
        _type_: issues found
    """
    print('---\tQuerying for Results\t---')
    return sonar.issues.search_issues(componentKeys=project, branch="main")


def start_sonarqube():
    """Starts sonarqube in the background, and waits 40 seconds for it to spin up before continuing
    """
    print('---\tSonarqube Server Starting\t---')
    # subprocess.Popen(
    #     ["/Users/sonarqube-10.0.0.68432/bin/macosx-universal-64/sonar.sh", "console"], stdout=subprocess.DEVNULL)
    # # Sleeps until the server has started.
    # time.sleep(40)
    print('---\tSonarqube Server Started\t---')
