from flask import render_template, Flask, request, redirect, session
from flask_session import Session

app = Flask(__name__)
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

lobbies = {} #A dictionary to hold our lobby sessions... what's a database???

class lob:
    def __init__(self):
        self.isReady=False
        self.lobby=[]
        self.sesCount = 0

    def give_num(self):
        self.sesCount += 1
        return self.sesCount - 1

def get_new_lobby_num():
    return len(lobbies.keys())

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def index():
    #The home page. Will act as a How To page with a box that sends the post to get the lobby number for the user
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        #Get a new lobby num and redirect to that lobby's URL
        if request.form['lobbyNum'] != 'false':
            return redirect('/lobby/' + request.form['lobbyNum'])
        else:
            return redirect('/lobby/' + str(get_new_lobby_num()))

@app.route('/lobby/<lobbyNum>', methods=['GET', 'POST'])
def lobby(lobbyNum):
    global lobbies
    if lobbyNum not in lobbies.keys():
        #Check to see if this is a new lobby
        lobbies[lobbyNum] = lob()

    try:
        a = session['id']
        print(a)
    except:
        session['id'] = lobbies[lobbyNum].give_num()

    if lobbies[lobbyNum].isReady:
        return redirect('/game/<lobbyNum>')

    isReady = bool(request.args.get('ready'))
    if isReady:
        #This would be the first instance of a player being ready. So assign the commander here
        lobbies[lobbyNum].isReady = True
        return redirect('/game/<lobbyNum>')

    else:
        return render_template('lobby.html', lobbyNum=lobbyNum)

@app.route('/game/<lobbyNum>', methods=['GET', 'POST'])
def game(lobbyNum):
    return 'Hi!'

if __name__ == "__main__":
    app.run()