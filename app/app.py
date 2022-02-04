from flask import render_template, Flask, request, redirect, session
from flask_session import Session
import random

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config["USER_PERMANENT_SESSION"] = False
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

@app.route('/disconnect/<lobbyNum>')
def disconnect(lobbyNum):
    global lobbies
    del lobbies[lobbyNum]

@app.route('/lobby/<lobbyNum>', methods=['GET', 'POST'])
def lobby(lobbyNum):
    global lobbies
    if lobbyNum not in lobbies.keys():
        #Check to see if this is a new lobby
        lobbies[lobbyNum] = lob()
        print('Created a new session')

    try:
        id = session['id']
        print(f'Session {id} is in lobby #{lobbyNum}')
    except:
        session['id'] = lobbies[lobbyNum].give_num()
        id = session['id']
        print('Gave this session a new lobby num')

    if id not in lobbies[lobbyNum].lobby:
        lobbies[lobbyNum].lobby.append(session['id'])

    if lobbies[lobbyNum].isReady:
        return redirect('/game/' + str(lobbyNum))

    isReady = bool(request.args.get('ready'))
    if isReady:
        #This would be the first instance of a player being ready. So assign the commander here
        lobbies[lobbyNum].isReady = True
        commanderID = random.choice(lobbies[lobbyNum].lobby)
        lobbies[lobbyNum].commandID = commanderID
        return redirect('/game/' + str(lobbyNum))

    else:
        personCount=len(lobbies[lobbyNum].lobby)
        return render_template('lobby.html', lobbyNum=lobbyNum, personCount=personCount)

@app.route('/game/<lobbyNum>', methods=['GET', 'POST'])
def game(lobbyNum):
    if lobbies[lobbyNum].commandID == session['id']:
        return '<h1>You get a command</h1>'
    else:
        return '<h1>no command for you</h1>'

if __name__ == "__main__":
    app.run()