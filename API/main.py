from flask import Flask, request
import json
app = Flask(__name__)

@app.route("/")
def hello():
    return "Maybe serve client from this endpoint"

@app.route("/route")
def route():
    origin = request.args.get('origin')
    dest = request.args.get('dest')
    dic = {
	'origin': origin,
	'dest': dest,
	'energy': 42
    }
    return json.dumps(dic)




#@app.route("/test/<int:num>")
#def test(num):
    #return str(testfunc(num,2))




def testfunc(x, y):
    return x ** y 

