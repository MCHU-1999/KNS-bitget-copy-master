from threading import Thread
import requests
from flask import Flask, request, jsonify, render_template
import json
from dotenv import load_dotenv


app = Flask('')

@app.route('/')
def main():
    return "Your bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()


# @app.route("/calcAPI", methods=['POST']) 
# def copySimulate():
#     data = json.loads(request.data)
#     print(data)
