# Copyright 2021 Google LLC
# Copyright 2022 Nils Knieling
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

###############################################################################
# This function will remove the billing account associated
# with the project if the cost amount is higher than the budget amount.
#
# Source:
# https://github.com/GoogleCloudPlatform/python-docs-samples
###############################################################################

import base64
import json
import google.auth
import os
import slack
from google.cloud import billing
from google.cloud import secretmanager

PROJECT_ID = google.auth.default()[1]
cloud_billing_client = billing.CloudBillingClient()

client          = secretmanager.SecretManagerServiceClient()
github_secret   = f"projects/{PROJECT_ID}/secrets/github-token/versions/latest"
github_response = client.access_secret_version(name=github_secret)
github_token    = github_response.payload.data.decode("UTF-8")
slack_secret    = f"projects/{PROJECT_ID}/secrets/slack-token/versions/latest"
slack_response  = client.access_secret_version(name=slack_secret)
slack_token     = slack_response.payload.data.decode("UTF-8")

slack_client = slack.WebClient(token=slack_token)


def notify_slack(data, context, channel):
    pubsub_message = data

    # For more information, see
    # https://cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications#notification_format
    try:
        notification_attr = json.dumps(pubsub_message['attributes'])
    except KeyError:
        notification_attr = "No attributes passed in"

    try:
        notification_data = base64.b64decode(data['data']).decode('utf-8')
    except KeyError:
        notification_data = "No data passed in"

    # This is just a quick dump of the budget data (or an empty string)
    # You can modify and format the message to meet your needs
    budget_notification_text = f'{notification_attr}, {notification_data}'

    try:
        slack_client.api_call(
            'chat.postMessage',
            json={
                'channel': channel,
                'text'   : budget_notification_text
            }
        )
    except SlackApiError:
        print('Error posting to Slack')


def scale_down(data: dict, context):
    pubsub_data = base64.b64decode(data["data"]).decode("utf-8")
    print(f"Data: {pubsub_data}")

    pubsub_json = json.loads(pubsub_data)
    cost_amount = pubsub_json["costAmount"]
    budget_amount = pubsub_json["budgetAmount"]

    if cost_amount <= budget_amount:
        print(f"No action necessary. (Current cost: {cost_amount})")
        return
    from github import Github

    # First create a Github instance:

    # using an access token
    github = Github(github_token)

    project_biling_info = cloud_billing_client.update_project_billing_info(request)
    print(f"Billing disabled: {project_biling_info}")
