from routes.api import API_PATH
from flask_cors import CORS
from flask import Flask
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)
app.register_blueprint(API_PATH)

if __name__ == '__main__':
    print(os.environ.get("PORT"), os.environ.get("HOST"))
    print("Running Server -- " + "Host:" +
          os.environ.get("HOST") + ":" + os.environ.get("PORT"),)
    app.run(host=os.environ.get("HOST"),
            port=os.environ.get("PORT"), debug=True)
