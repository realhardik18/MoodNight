from flask import Flask,jsonify

app=Flask(__name__)

@app.route('/')
def test():
    return 'hello world!'

app.run(debug=True)