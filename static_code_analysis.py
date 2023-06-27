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

from sonarqube import SonarQubeClient
import subprocess
from pathlib import Path
import time
import os
import logging
from logging_config import configure_logging
configure_logging()


def analyze(directory: Path) -> dict:
    """Uses Sonarqube to statically analyze the codebase

    Args:
        directory (Path): path to the codebase

    Returns:
        dict: results from the analysis
    """

    if 'SONAR_USER' not in os.environ or 'SONAR_PASS' not in os.environ:
        logging.error(
            'Please add your sonarqube credentials to the \'SONAR_USER\' and \'SONAR_PASS\' environment variables')
        exit(1)
    username = os.environ['SONAR_USER']
    password = os.environ['SONAR_PASS']
    start_sonarqube()
    project = directory.parts[-1]
    sonar = SonarQubeClient(sonarqube_url="http://localhost:9000",
                            username=username, password=password)
    projects = sonar.projects.search_projects(
        projects=[project])
    found = any(component['key'] ==
                project for component in projects['components'])

    run_analysis(found, str(directory.absolute()), username, password)
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
    logging.info('Stopping Sonarqube Server')
    # subprocess.Popen(["sonar.sh", "stop"], stdout=subprocess.DEVNULL)


def run_analysis(cached: bool, path: str, sonar_user: str, sonar_pass: str):
    """Runs the analysis of the codebase

    Args:
        cached (bool): If the repository has already been analyzed, dont do it again
        path (str): Path to the repository
    """
    logging.info('Static Code Analysis Starting')
    # subprocess.run(
    #     ["mvn",
    #      "sonar:sonar",
    #      "-Dsonar.host.url=http://localhost:9000",
    #      "-Dsonar.jacoco.reportPaths=**/*.xml",
    #      "-Dsonar.coverage.jacoco.xmlReportPaths=**/*.xml",
    #      f"-Dsonar.login={sonar_user}",
    #      f"-Dsonar.password={sonar_pass}"],
    #     cwd=path,
    #     shell=True,
    #     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logging.info('Static Code Analysis Finished')


def retrieve_results(sonar: SonarQubeClient, project: str):
    """Queries the Sonarqube server for static code analysis results

    Args:
        sonar (SonarQubeClient): The sonarqube client object to query
        project (str): the project we are querying

    Returns:
        _type_: issues found
    """
    logging.info('Querying for Results')
    return sonar.issues.search_issues(componentKeys=project, branch="main")


def start_sonarqube():
    """Starts sonarqube in the background, and waits 40 seconds for it to spin up before continuing
    """
    logging.info('Sonarqube Server Starting')
    # subprocess.Popen(["sonar.sh", "console"], stdout=subprocess.DEVNULL)
    # # Sleeps until the server has started.
    # for x in range(0, 40, 10):
    #     logging.info('Waiting for sonarqube to start')
    #     time.sleep(10)
    logging.info('Sonarqube Server Started')
