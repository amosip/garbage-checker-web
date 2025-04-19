from flask import Flask, render_template, request, redirect, url_for
from garbage_checker.checker import process_folder
from garbage_checker.config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        folder_path = request.form.get('folder_path')
        if folder_path:
            garbled_files = process_folder(folder_path)
            return render_template('index.html', garbled_files=garbled_files)
    return render_template('index.html', garbled_files=None)

if __name__ == '__main__':
    app.run(debug=True)