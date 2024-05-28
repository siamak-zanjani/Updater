''' the updater.py is a script ran by the Dockerfile in the parent directory. It is responsible for:
    - Handling webhooks sent by BitBucket when certain events happen on the repository

    Bitbucket Webhooks:
    Repo -> Settings -> Webhooks -> Create webhook
        url: http://docs.octasic.com/update
        Test connection: to debug
        Repository/Pull request Events and their Payloads

Sources:
    - Event payloads sent by BitBucket: https://support.atlassian.com/bitbucket-cloud/docs/event-payloads/
    - Complete POST header and body can be found in the Webhooks tab of the repo's settings and under 
        "Last success/failure" of the hook that was set-up: 
        https://bitbucket.octasic.com:8443/plugins/servlet/webhooks/projects/OADF/repos/oadf_docs
'''
from flask import Flask, request
import subprocess
import json  # Import the json module
import requests
import subprocess
from os.path import join
import os
import threading

app = Flask(__name__)

# The mapped volume path in the 'docker-compose.yaml' file
DOCKER_REPO_PATH = '/root/repo'

def update_commit_status(workspace, repo_slug, commit_id, state, description, access_token):
    # url = f"https://bitbucket.octasic.com:8443/2.0/repositories/{workspace}/{repo_slug}/commit/{commit_id}/statuses/build"
    url = f"https://bitbucket.octasic.com:8443/rest/build-status/1.0/commits/{commit_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "state": state,
        "description": description,
        "key": description,
        "logs": description,
        "url": "https://docs.octasic.com"  # URL to more details or logs
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

@app.route('/update', methods=['GET','POST'])
def webhook():
    if request.method == 'POST':
        # Parse the JSON payload
        payload = json.loads(request.data)
        
        # Extract workspace and repo_slug from the payload
        workspace = payload['repository']['project']['key']
        repo_slug = payload['repository']['slug']
        # Replace with your actual access token
        access_token = "BBDC-MzYxMzkxODk0MzgwOuPuLSJA5MxtYFCxUUYTOI0jzjUu"
        
        if request.headers.get('X-Event-Key') == 'diagnostics:ping':
            return 'Ping test received', 200
        # Example: Check for a specific event  
        
        if payload.get('eventKey') == 'repo:refs_changed':
            for change in payload['changes']:
                if change['ref']['id'] == "refs/heads/master":
                    commit_id = change['toHash']  # Get the commit displayId
                    subprocess.call(['git', '-C', DOCKER_REPO_PATH, 'pull'])
                    update_commit_status(workspace,repo_slug,commit_id, "SUCCESSFUL", f'Update executed on master branch for commit {commit_id}', access_token)
                    return f'Git pull executed on master branch for commit {commit_id}', 200
        
        # Check for a pull request merged into the master branch
        
        elif payload.get('eventKey') == 'pr:merged':
            if payload['pullRequest']['toRef']['id'] == "refs/heads/master":
                commit_id = payload['pullRequest']['toRef']['latestCommit']  # Get the commit displayId
                subprocess.call(['git', '-C', DOCKER_REPO_PATH, 'pull'])
                update_commit_status(commit_id, "SUCCESSFUL", f'Update executed for merged pull request into master for commit {commit_id}', access_token)
                return f'Git pull executed for merged pull request into master for commit {commit_id}', 200
        else:
            return 'Ignored event', 200
    if request.method == 'GET':
        subprocess.call(['git', '-C', DOCKER_REPO_PATH, 'pull'])
        return 'Success', 200

def build_documentation():
    ''' Threaded function to run the documentation builder
    TODO: Add a log or change the execution of the function (not in a thread so we can return
    to the user the errors)
    '''
    subprocess.run(['python', 'build.py'], cwd = join(DOCKER_REPO_PATH, "build_tools"), 
                    capture_output=True, timeout=30000)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    ''' Generate webhook called by BitBucket on 'release/#' branch creation, push, tag, delete branch
    and merging of a PR. Here we only handle: push, branch create and PR merge
    '''
    if request.method == 'GET':
        threading.Thread(target=build_documentation).start()
        return "Success", 200
    
    if request.method == 'POST':
        # Parse the JSON payload
        payload = json.loads(request.data)

        # Handle ping for the BitBucket 'Test Connection' button in WebHooks: 
        if request.headers.get('X-Event-Key') == 'diagnostics:ping':
            return 'Ping test received', 200
        
        # Check for a Release branch: New branch, push to branch
        if payload.get('eventKey') == 'repo:refs_changed':
            for change in payload['changes']:
                branch_name = change['ref']['id']
                if "refs/heads/release/" in branch_name:
                    threading.Thread(target=build_documentation).start()
                    return "Success", 200
        
        # Check for a Release branch: Pull request merged
        elif payload.get('eventKey') == 'pr:merged':
            branch_name = payload['pullRequest']['toRef']['id']
            if "refs/heads/release/" in branch_name:
                threading.Thread(target=build_documentation).start()
                return "Success", 200
        else:
            return 'Ignored event', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
