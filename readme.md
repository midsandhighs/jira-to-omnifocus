# Jira to OmniFocus Sync

A script to synchronize Jira tasks with OmniFocus.

## What does it do?

This script connects to the Jira REST API via basic auth to pull down Jira tasks associated with the current user.

See the configuration section below for details on setting up.

## Features

- Only projects listed in the yaml file will be retrieved.
- Only tasks associated with the current user will be retrieved.
- If a task cannot be found that starts with the current Jira task key (e.g. PROJ-1),
then a new task is created within OmniFocus for the current project.
- If a task is found that matches the current Jira task key and that task is marked as "Done", "Closed", or "Resolved"
then the task is marked s complete within OmniFocus.
- Only tasks within the context set in the yaml file are completed. Others will be ignored.

## Configuration

Add a file named `.jira-to-omnifocus.yml` in your home diretory (e.g. `~/.jira-to-omnifocus.yml`) with the following information:

        ---
        jira:
            hostname: <jira-hostname>
            username: <username>
            password: <password>
            maxResults: 100
            projects:
                - PROJ1
                - PROJ2
                - PROJ3
        omnifocus:
            context: 'Jira'


- **jira.hostname**: The Jira hostname to connect to.
- **jira.username**: The username to connect with
- **jira.password**: The password to connect with
- **jira.maxResults**: The max number of tasks to pull down for each project.
- **jira.projects**: A list of projects to sync with.
- **omnifocus.context**: The context to associate jira tasks with.

## Credits

The `asrun` and `asquote` routines come from [Dr. Drang](http://www.leancrew.com/all-this/2013/03/combining-python-and-applescript/)

