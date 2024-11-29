from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for sessions

# Configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'txt', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        participant_names = request.form.get('participant_names', '').split('\n')
        participant_names = [name.strip() for name in participant_names if name.strip()]

        files = request.files.getlist('participant_files')

        participants = []

        # Add participants from names
        for name in participant_names:
            participants.append({'name': name, 'file': None})

        # Add participants from files
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                participants.append({'name': filename, 'file': filename})

        # Store participants in session or global variable
        session['participants'] = participants

        # Get number of rounds
        num_rounds = request.form.get('num_rounds')
        try:
            num_rounds = int(num_rounds)
        except:
            num_rounds = len(participants) - 1

        session['num_rounds'] = num_rounds
        session['current_round'] = 1
        session['matchups'] = []
        session['scores'] = {p['name']: 0 for p in participants}
        session['bye_history'] = []
        session['matchup_history'] = []  # Store all matchups for the tournament

        # Generate initial matchups
        generate_matchups()

        return redirect(url_for('tournament'))

    return render_template('index.html')


def generate_matchups():
    import random
    participants = session['participants']
    scores = session['scores']
    current_round = session['current_round']
    bye_history = session.get('bye_history', [])
    matchup_history = session.get('matchup_history', [])

    # Sort participants by score, then randomize within the same score group
    score_groups = {}
    for p in participants:
        s = scores[p['name']]
        score_groups.setdefault(s, []).append(p)

    sorted_participants = []
    for s in sorted(score_groups.keys(), reverse=True):
        group = score_groups[s]
        random.shuffle(group)
        sorted_participants.extend(group)

    # Generate pairings
    matchups = []
    unpaired = sorted_participants.copy()

    # If odd number of participants, assign a bye
    if len(unpaired) % 2 != 0:
        # Find a participant who hasn't had a bye yet
        for p in unpaired:
            if p['name'] not in bye_history:
                bye_player = p
                bye_history.append(bye_player['name'])
                unpaired.remove(bye_player)
                matchups.append({'p1': bye_player, 'p2': None})
                break
        else:
            # All players have had a bye, assign to the last player
            bye_player = unpaired.pop()
            matchups.append({'p1': bye_player, 'p2': None})

    # Pair the remaining participants, avoiding duplicate matchups
    while unpaired:
        p1 = unpaired.pop(0)
        valid_opponents = [p for p in unpaired if {p1['name'], p['name']} not in matchup_history]
        if valid_opponents:
            p2 = valid_opponents[0]
            unpaired.remove(p2)
            matchups.append({'p1': p1, 'p2': p2})
            matchup_history.append({p1['name'], p2['name']})
        else:
            # If no valid opponents are found, reshuffle and retry
            unpaired.append(p1)
            random.shuffle(unpaired)

    # Store matchups and update session
    session['matchups'] = matchups
    session['current_matchup_index'] = 0
    session['bye_history'] = bye_history
    # Convert sets in matchup_history to tuples for JSON serialization
    session['matchup_history'] = [list(match) for match in matchup_history]


@app.route('/tournament', methods=['GET', 'POST'])
def tournament():
    if 'participants' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Process the result of the previous matchup
        winner = request.form.get('winner')
        if winner:
            scores = session['scores']
            scores[winner] += 1
            session['scores'] = scores

        # Move to next matchup
        session['current_matchup_index'] += 1

    current_matchup_index = session['current_matchup_index']
    matchups = session['matchups']

    if current_matchup_index >= len(matchups):
        # Round is over, show round summary
        return redirect(url_for('round_summary'))

    matchup = matchups[current_matchup_index]
    total_matches = len(matchups)
    match_number = current_matchup_index + 1

    return render_template('tournament.html', matchup=matchup, round=session['current_round'],
                           match_number=match_number, total_matches=total_matches)


@app.route('/round_summary', methods=['GET', 'POST'])
def round_summary():
    if 'participants' not in session:
        return redirect(url_for('index'))

    scores = session.get('scores', {})
    participants = session.get('participants', [])
    rankings = sorted(participants, key=lambda x: (-scores[x['name']], x['name']))

    if request.method == 'POST':
        # Start next round or end tournament
        if session['current_round'] >= session['num_rounds']:
            # Tournament is over
            return redirect(url_for('summary'))
        else:
            # Start next round
            session['current_round'] += 1
            generate_matchups()
            return redirect(url_for('tournament'))

    return render_template('round_summary.html', rankings=rankings, scores=scores, round=session['current_round'],
                           num_rounds=session['num_rounds'])


@app.route('/summary')
def summary():
    scores = session.get('scores', {})
    participants = session.get('participants', [])
    rankings = sorted(participants, key=lambda x: (-scores[x['name']], x['name']))
    return render_template('summary.html', rankings=rankings, scores=scores)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
