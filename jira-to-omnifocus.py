# Jira to OmniFocus

import yaml
import subprocess
from jira import JIRA
from os.path import expanduser

opts = {}
optsPath = expanduser("~/.jira-to-omnifocus.yml")

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

def complete_task(projectKey, taskKey):

    ascript = '''
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
        '''.format(asquote(projectKey + " - "), asquote(taskKey), asquote(opts['omnifocus']['context']))

    asrun(ascript)

def create_task(projectKey, taskKey, taskName):


    ascript = '''
tell application "OmniFocus"

	set theTaskKey to {1}
	set theTaskName to {2}
	set theContext to {3}
	set theProjectKey to {0}

	try
		set theProject to first flattened project of default document whose name starts with theProjectKey
	on error theError
	    display dialog "Project does not exist: " & theProjectKey
	end try

	if not (exists (first flattened task of default document whose name starts with theTaskKey)) then

		-- Create the transport text
		set theTransportText to theTaskName & " @" & theContext & " ::" & name of theProject

		-- parse into a task
		parse tasks into default document with transport text theTransportText

	end if

end tell
        '''.format(asquote(projectKey + " - "), asquote(taskKey), asquote(taskName), asquote(opts['omnifocus']['context']))

    asrun(ascript)

with open(optsPath, 'r') as optsFile:
    try:
        opts = yaml.load(optsFile)
    except yaml.YAMLError as ex:
        print(ex)
        exit()

print "Connecting to {}...".format(opts['jira']['hostname'])

jira = JIRA(server=opts['jira']['hostname'],basic_auth=(opts['jira']['username'], opts['jira']['password']))

projects = opts['jira']['projects']

for project in projects:
    print("Reviewing project {}...".format(project))
    jql = "project=\"{}\" and assignee = currentUser()".format(project)
    for issue in jira.search_issues(jql,maxResults=opts['jira']['maxResults']):
        if str(issue.fields.status) in ["Done", "Closed", "Resolved"]:

            # print ("-- {}, {}".format(issue.key, issue.fields.status))
            complete_task(project, issue.key)

        else:

            # print ("-- {0}, {1}, {2}".format(issue.key, issue.fields.summary, issue.fields.status))
            create_task(project, issue.key, issue.key + " " + issue.fields.summary)

