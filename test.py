from flask import Flask, jsonify, render_template, request
from hashtag import newDP as DP

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    returnval = 'Please enter a hashtag to segment.'
    if request.method == 'POST':
    	if request.form['text']:
		returnval = DP.result(request.form['text'])
    return render_template('index.html',returval=returnval)


if __name__ == '__main__':
    app.run()
