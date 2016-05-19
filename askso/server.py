import json
import traceback
import os
from flask import Flask, request

from execute import execute

app = Flask(__name__, static_url_path='',
            static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                       'static'))


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/run', methods=['POST'])
def run():
    # noinspection PyBroadException
    try:
        return json.dumps(execute(request.get_data().decode('utf8')))
    except:
        return traceback.format_exc(), 500


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
