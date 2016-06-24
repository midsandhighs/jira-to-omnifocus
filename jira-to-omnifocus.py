# Jira to OmniFocus

import yaml
import subprocess
from sys import argv
from jira import JIRA
from os.path import expanduser

opts = {}
optsPath = expanduser("~/.jira-to-omnifocus.yml")

DEFAULT_MAX_RESULTS = 100
DEFAULT_JQL = 'project="{}" and assignee = currentUser()'
DEFAULT_COMPLETED_STATUS = ['Done', 'Closed', 'Resolved']

NOTIFICATION_SCRIPT = '''

display notification {0} with title {1}

'''

COMPLETE_SCRIPT = '''
tell application "OmniFocus"

    set theTaskKey to {1}
    set theProjectKey to {0}
    set theContext to {2}

    tell default document

        try
            set theProject to first flattened project whose name starts with theProjectKey
        on error theError
            return theError
        end try

        if exists (first flattened task whose name starts with theTaskKey) then

            set selectedTask to first flattened task whose name starts with theTaskKey

            if name of context of selectedTask = theContext then
                if (not completed of selectedTask) then
                    set completed of selectedTask to true
                end if
            end if

        end if

    end tell

end tell
'''

CREATE_SCRIPT = '''
tell application "OmniFocus"

	set theTaskKey to {1}
	set theTaskName to {2}
	set theContext to {3}
	set theProjectKey to {0}

	try
		set theProject to first flattened project of default document whose name starts with theProjectKey
	on error theError
	    -- display dialog "Project does not exist: " & theProjectKey
	    return theError
	end try

	if not (exists (first flattened task of default document whose name starts with theTaskKey)) then

		-- Create the transport text
		set theTransportText to theTaskName & " @" & theContext & " ::" & name of theProject
		set theTransportText to theTransportText & " //https://sensory5.atlassian.net/browse/" & theTaskKey

		-- parse into a task
		parse tasks into default document with transport text theTransportText

	end if

end tell
'''

def asrun(ascript):
  "Run the given AppleScript and return the standard output and error."

  osa = subprocess.Popen(['osascript', '-'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
  return osa.communicate(ascript)[0]

def asquote(astr):
  "Return the AppleScript equivalent of the given string."

  astr = astr.replace('"', '" & quote & "')
  return '"{}"'.format(astr)

def notify(message, title):
    asrun(NOTIFICATION_SCRIPT.format(asquote(message),
                                     asquote(title)))

def complete_task(projectKey, taskKey):
    "Complete the task if found in OmniFocus."

    ascript = COMPLETE_SCRIPT.format(asquote(projectKey + " - "),
                                     asquote(taskKey),
                                     asquote(opts['omnifocus']['context']))

    asrun(ascript)

def create_task(projectKey, taskKey, taskName):
    "Create the task if not found in OmniFocus."

    ascript = CREATE_SCRIPT.format(asquote(projectKey + " - "),
                                   asquote(taskKey),
                                   asquote(taskName),
                                   asquote(opts['omnifocus']['context']))

    asrun(ascript)

# Open the configuration file and retrieve options
with open(optsPath, 'r') as optsFile:
    try:
        opts = yaml.load(optsFile)
    except yaml.YAMLError as ex:
        print(ex)
        exit()

# Capture any arguments and replace them as
# the projects to be retrieved
if len(argv) > 1:
    projects = argv[1:]
else:
    projects = opts['jira']['projects']

showNotification = opts['jira'].get('showNotifications', False)

# Connect to Jira and retrieve issues
# print "Connecting to {}...".format(opts['jira']['hostname'])
if showNotification:
    notify("Connecting to {0}".format(opts['jira']['hostname']), "Jira to OmniFocus")

jira = JIRA(server=opts['jira']['hostname'],
            basic_auth=(opts['jira']['username'], opts['jira']['password']))

for project in projects:

    # print("Reviewing project {}...".format(project))
    if showNotification:
        notify("Syncing {}".format(project), "Jira to OmniFocus Project")

    jql = opts['jira'].get('jql', DEFAULT_JQL).format(project)
    statusOpts = opts['jira'].get('completedStatus', DEFAULT_COMPLETED_STATUS)
    maxResults = opts['jira'].get('maxResults', DEFAULT_MAX_RESULTS)

    for issue in jira.search_issues(jql, maxResults=maxResults):


        if str(issue.fields.status) in statusOpts:
            # print ("-- {}, {}".format(issue.key, issue.fields.status))
            complete_task(project, issue.key)
        else:
            # print ("-- {0}, {1}, {2}".format(issue.key, issue.fields.summary, issue.fields.status))
            create_task(project, issue.key, issue.key + " " + issue.fields.summary)

