from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from slackclient import SlackClient

import os

from model import Model, DecimalJSONEncoder

app = Flask(__name__)
app.json_encoder = DecimalJSONEncoder
CORS(app)

app.model = Model()
app.slack_client = SlackClient(os.environ.get('SLACK_API_KEY'))


def is_request_valid(req):
    is_token_valid = req.form['token'] == os.environ.get('SLACK_VERIFICATION_TOKEN')
    is_team_id_valid = request.form['team_id'] == os.environ.get('SLACK_TEAM_ID')
    return is_token_valid and is_team_id_valid


@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "healthy"}), 200


@app.route('/messages', methods=['GET'])
def messages():
    return jsonify(app.model.get())


@app.route('/slack', methods=['POST'])
def inbound():
    if not is_request_valid(request):
        abort(400)

    message = request.form.get('text')
    message_id = app.model.put(message)
    if message_id:
        return jsonify(
            response_type='in_channel',
            text='Published {} to live with id {}'.format(message, message_id),
        )
    else:
        abort(400)


@app.route('/slack_delete', methods=['POST'])
def slack_delete():
    if not is_request_valid(request):
        abort(400)

    message_id = request.form.get('text')
    app.model.delete(message_id)
    return jsonify(
        response_type='in_channel',
        text='Deleted messaged {}'.format(message_id)
    )


if __name__ == '__main__':
    app.run()
