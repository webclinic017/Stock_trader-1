from flask import Flask

app = Flask(__name__)

# Below import is placed here to stop circular import
from app import routes
