from flask import Flask, g

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)


@app.before_request
def before_request():
    pass


@app.after_request
def after_request():
    pass


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
