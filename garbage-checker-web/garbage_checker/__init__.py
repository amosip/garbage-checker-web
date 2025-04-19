from flask import Flask

app = Flask(__name__)

from garbage_checker import routes