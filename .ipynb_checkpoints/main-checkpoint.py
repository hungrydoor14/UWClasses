from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    with open("homepage.html") as f:
        html = f.read()
    return html
    
# SOURCE: Gurmail Singh's CS320 class
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!
# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
