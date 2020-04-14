# Jira to OmniFocus Sync

A script to synchronize Jira issues with OmniFocus.

This appears to be out of date - and doesn't 

## What does it do?

This script connects to the Jira REST API via basic auth to
sync Jira issues with OmniFocus.

It uses `osascript` to run dynamic AppleScript snippets that update and create tasks in OmniFocus.

See the configuration section below for details on how to configure the options.

## Features

- Only projects listed in the `.jira-to-omnifocus.yml` file will be retrieved.
    - A synced project must exist in OmniFocus before running the script
    - OmniFocus project names should start with the Jira project key followed by a hyphen (e.g. "PROJ - ")
    - If you pass a set of arguments to the script (e.g. `jira-to-omnifocus.py PROJ1 PROJ2`), then those arguments will override the configured projects to be retrieved (i.e. it will only retrieve the projects with keys that match the passed in arguments)
- Only issues associated with the currently logged in Jira user will be retrieved.
- If an OmniFocus task cannot be found that starts with the current Jira issue key (e.g. PROJ-1),
then a new task is created within OmniFocus for the current project.
    - New tasks are assigned the configured context
    - New tasks are named with the Jira issue key followed by the issue summary text (e.g. "PROJ-1 My project task")
- If a task is found that matches the current Jira issue key and issue status is one of the
status indicators found in the `completedStatus` config, then the OmniFocus task is marked as complete.
- Only OmniFocus tasks within the configured context are completed. Others will be ignored.

## Useage

This is a one-way sync from Jira. I tend to review my Jira related tasks in OmniFocus to keep me on track
and help me plan my day. However, I always update the Jira issue inside of Jira itself and never in OmniFocus.

This pattern works fine for me and let's me manage team related tasks on the team Jira.

To run the script I created a simple [Alfred](https://www.alfredapp.com/) workflow that runs the python script on demand.

I'm sure this could be automated with something like `launchd`, but I didn't want syncs happening in the background.

## Requirements

- [PyYaml](https://pypi.python.org/pypi/PyYAML) 3.11+

        pip install PyYaml

- [Jira](https://pypi.python.org/pypi/jira) 1.07+

        pip install jira

## Configuration

Add a file named `.jira-to-omnifocus.yml` in your home diretory (e.g. `~/.jira-to-omnifocus.yml`) with the following information:

        ---
        jira:
            hostname: <jira-hostname>
            username: <username>
            password: <password>
            jql: 'project="{}" and assignee = currentUser()'
            maxResults: 100
            showNotifications: true
            projects:
                - PROJ1
                - PROJ2
                - PROJ3
            completedStatus:
                - Done
                - Closed
                - Resolved
        omnifocus:
            context: 'Jira'


- **jira.hostname**: The Jira hostname to connect to. **(REQUIRED)**
- **jira.username**: The username to connect with. **(REQUIRED)**
- **jira.password**: The password to connect with. **(REQUIRED)**
- **jira.projects**: A list of projects to sync with. **(REQUIRED)**
- **omnifocus.context**: The context to associate jira tasks with. **(REQUIRED)**
- **jira.jql**: The jql passed to Jira. Note that you must have a placeholder for the project key in the jql.
    - _(optional, default: `project="{}" and assignee = currentUser()`)_
    - An example alternative JQL is to only show assigned tasks for the given project in open sprints ordered by priority:

            project="{}" and assigneed = currentUser() and sprint in openSprints() ordered by priority desc

- **jira.maxResults**: The max number of tasks to pull down for each project. _(optional, default: 100)_
- **jira.completedStatus**: The list of status indicators that constitute a completed task. _(optional, default: Done, Closed, Resolved)_
- **jira.showNotifications**: If true, shows a notification for each project synced in the loop. _(optional, default: false)_

## Credits

The `asrun` and `asquote` routines come from [Dr. Drang](http://www.leancrew.com/all-this/2013/03/combining-python-and-applescript/)

