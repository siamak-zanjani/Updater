# Webhook Flask Application Summary

This Python script creates a Flask application to act as a webhook for handling Bitbucket repository events.

## Overview

- **Technology**: Flask web framework, Python.
- **Purpose**: Respond to Bitbucket webhook events with specific actions.
- **Primary Actions**: Execute `git pull` commands and update commit statuses in Bitbucket.

## Functionality

### Webhook Endpoint
- **Endpoint**: `/update`
- **Supported Methods**: `GET`, `POST`

### POST Method
- **Payload Handling**: Parses JSON payload from Bitbucket webhook.
- **Event Handling**:
  - **Push to Master Branch**: Executes `git pull` and updates commit status when changes are pushed to the `master` branch.
  - **Pull Request Merged to Master**: Executes `git pull` and updates commit status when a pull request is merged into the `master` branch.
- **Response**: Returns a success message with the commit ID.

### GET Method
- **Action**: Executes `git pull` in the specified directory (`/root/repo`).
- **Response**: Returns 'Success'.

### Webhook Endpoint
- **Endpoint**: `/generate`
- **Supported Methods**: `GET`, `POST`

### POST Method
- **Payload Handling**: Parses JSON payload from Bitbucket webhook.
- **Event Handling**:
  - **Push to Release Branch**: Executes `build.py` which rebuilds branch
  - **Pull Request Merged to Release**: Executes `build.py` which rebuilds the content when a PR is merged to 'release' branch of a documentation repo
- **Response**: Returns a success.

### GET Method
- **Action**: Executes `build.py` which rebuilds all branches.
- **Response**: Returns 'Success'.

### Commit Status Update
- **Function**: `update_commit_status`
- **Purpose**: Makes an API call to Bitbucket to update the commit's build status.
- **Parameters**: Includes workspace, repository slug, commit ID, state, description, and an access token.
