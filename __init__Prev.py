from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, I really love Digital Ocean!"
if __name__ == "__main__":
    app.run(port=80)
