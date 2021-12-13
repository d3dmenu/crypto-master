# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import json
import logging

from flask import Flask, request, abort
from src.functions.utils import extract_data, decision, settings

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    FlexSendMessage, TextSendMessage,
)
from src.task import jobs


# Channel Access Token
line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)

# Channel Secret
handler = WebhookHandler(settings.CHANNEL_SECRET)

app = Flask(__name__)

""" Disable console messages in Flask server """
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def heroku():
    return 'HEROKU BUILD SUCCESS.'


@app.route('/webhook', methods=['POST'])
def callback():
    # get request body as text
    body = request.get_json(silent=True, force=True)
    # extract data information from dialogflow
    data = extract_data(body)
    # finding case role for response to users
    response = decision(data)
    reply_message(response, data['reply_token'])
    return 'OK'


def reply_message(response: dict or str, reply_token: str):
    if type(response) == str:
        text_message = TextSendMessage(text=response)
        line_bot_api.reply_message(reply_token, text_message)

    elif type(response) == dict:
        mock = response['flex-mock'] % response['script']
        flex = json.loads(mock)

        reply_obj = FlexSendMessage(alt_text='(System) - Send Message', contents=flex)
        line_bot_api.reply_message(reply_token, reply_obj)


if __name__ == '__main__':
    jobs.schedule.start()
    app.run(debug=False)
