from flask import Flask
app = Flask(__name__)

# q1 - basic
@app.route('/hello')
def start():
    return ''

# q2
if __name__ == '__main__':
     app.run(port=8080)