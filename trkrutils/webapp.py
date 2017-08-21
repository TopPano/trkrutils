import threading
import webbrowser
from flask import Flask, render_template

DEFAULT_PORT = 4735
DEFAULT_AUTO_OPEN = True

def run(
    webdata_list,
    port = DEFAULT_PORT,
    auto_open = DEFAULT_AUTO_OPEN):
    app = Flask('')

    webdata_dict = dict((webdata['name'], webdata) for webdata in webdata_list)

    @app.route('/')
    def index():
        return render_template('index.html', data_list = webdata_list)

    @app.route('/result/<name>')
    def result(name):
        return render_template('result.html', data = webdata_dict[name])

    if auto_open:
        url = 'http://127.0.0.1:{0}'.format(port)
        threading.Timer(1.25, lambda: webbrowser.open(url)).start()

    app.run(port = port)
