from flask import render_template, Flask, request, redirect, session, jsonify
from flask_session import Session
import random
import datetime

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
    def reset(self):
        self.isReady = False
        self.lobby=[]
        self.sesCount = 0

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

    if request.method == 'GET':
        if lobbyNum not in lobbies.keys():
            lobbies[lobbyNum] = lob()
            print('Created a new session')

        session['id'] = lobbies[lobbyNum].give_num()
        print('Gave this session a new lobby num')

        lobbies[lobbyNum].lobby.append(session['id'])

        personCount=len(lobbies[lobbyNum].lobby)

        return render_template('lobby.html', lobbyNum=lobbyNum, personCount=personCount, sesID=session['id'])

    elif request.method == 'POST':

        if lobbies[lobbyNum].isReady:
            #This will be the auto redirect if we are ready, so people are not triggering a new command id to be made when they're ready
            personCount=len(lobbies[lobbyNum].lobby)
            
            payload = {
            'ready': lobbies[lobbyNum].isReady,
            'person_count': personCount
            }
            return jsonify(payload)

        else:
            data = request.get_json()
            if data[0]['isReady']:
                #This is triggered by the first person to say "Ready"
                #Thus, we choose the commandID here.
                lobbies[lobbyNum].commandID = random.choice(lobbies[lobbyNum].lobby)
                lobbies[lobbyNum].endTime = datetime.datetime.now() + datetime.timedelta(minutes=1)
                lobbies[lobbyNum].isReady = True

            personCount=len(lobbies[lobbyNum].lobby)
            payload = {
                'ready': lobbies[lobbyNum].isReady,
                'person_count': personCount
            }
            return jsonify(payload)


@app.route('/game/<lobbyNum>', methods=['GET', 'POST'])
def game(lobbyNum):
    if request.method == 'GET':
        sessionID=request.args['s']
        isCommand = str(lobbies[lobbyNum].commandID) == str(sessionID)
        command = ""
        lobbies[lobbyNum].switch = True

        if isCommand:
            #Get Command here
            command = random.choice([
                'Keep a finger pointed up for the round',
                'Stand up',
                'Give someone a high five',
                'Give someone the finger guns',
                'Act like you are rowing a canue',
            ])

        return render_template('game.html', isCommand=isCommand, lobbyNum=lobbyNum, sesID=sessionID, command=command)

    elif request.method == 'POST':
        t = lobbies[lobbyNum].endTime - datetime.datetime.now()
        secs = int(t.total_seconds())

        if (secs <= 0) and (lobbies[lobbyNum].switch):
            lobbies[lobbyNum].switch = False
            lobbies[lobbyNum].commandID = random.choice(lobbies[lobbyNum].lobby)
            lobbies[lobbyNum].endTime = datetime.datetime.now() + datetime.timedelta(minutes=1)
            lobbies[lobbyNum].isReady = True
        
        payload = {
            'timer' : secs,
            'switch': not lobbies[lobbyNum].switch
        }

        return jsonify(payload)

if __name__ == "__main__":
    app.run()