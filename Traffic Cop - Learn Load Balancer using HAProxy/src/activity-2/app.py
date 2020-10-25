from flask import Flask, request
import sys

PORT_NUMBER = sys.argv[1]

app = Flask(__name__)

@app.route('/')
def index():
	print(request.headers)
	return "Hi!! from server %s" % PORT_NUMBER

if __name__ == '__main__':
	app.run(port=sys.argv[1])

#Run the server in command line as follows:-
# python app.py <Unused port number>
#eg. python app.py 3000
