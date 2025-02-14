from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

# API configuration
API_KEY = '57c24b1094f64ebcadca6fac13969944'  # Replace with your actual API key
BASE_URL = 'https://api.football-data.org/v2/'
headers = {'X-Auth-Token': API_KEY}

# Premier League Teams for 2023/2024 with placeholder team IDs
team_ids = {
    'Arsenal': 57, 'Aston Villa': 58, 'Bournemouth': 1044, 'Brentford': 402, 'Brighton': 397, 'Burnley': 328,
    'Chelsea': 61, 'Crystal Palace': 354, 'Everton': 62, 'Fulham': 63, 'Liverpool': 64, 'Luton Town': 60,
    'Manchester City': 65, 'Manchester United': 66, 'Newcastle United': 67, 'Nottingham Forest': 68,
    'Sheffield United': 356, 'Tottenham Hotspur': 73, 'West Ham United': 74, 'Wolverhampton Wanderers': 76
}

@app.route('/')
def home():
    return render_template('index.html', teams=list(team_ids.keys()))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Retrieve team names from form data
        home_team = request.form['home_team']
        away_team = request.form['away_team']
        
        home_team_id = team_ids.get(home_team)
        away_team_id = team_ids.get(away_team)
        
        if home_team_id is None or away_team_id is None:
            return jsonify({"error": "Invalid team selection"}), 400
        
        # Prediction logic (e.g., using logistic regression and random forest)
        logreg_result = make_prediction(home_team_id, away_team_id, model='logistic')
        rf_result = make_prediction(home_team_id, away_team_id, model='random_forest')
        
        return render_template('result.html',
                               home_team=home_team,
                               away_team=away_team,
                               logreg_result=logreg_result,
                               rf_result=rf_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define your prediction logic function
def make_prediction(home_team_id, away_team_id, model='logistic'):
    # Get form and goals data
    home_form = get_recent_form(home_team_id)
    away_form = get_recent_form(away_team_id)
    
    home_goals_scored, home_goals_conceded = get_avg_goals(home_team_id)
    away_goals_scored, away_goals_conceded = get_avg_goals(away_team_id)
    
    # Simple rule-based logic for demonstration
    home_advantage = home_form + home_goals_scored - away_goals_conceded
    away_advantage = away_form + away_goals_scored - home_goals_conceded
    
    if model == 'logistic':
        prediction = "Home Win" if home_advantage > away_advantage else "Away Win" if home_advantage < away_advantage else "Draw"
    elif model == 'random_forest':
        # Placeholder for alternative model logic (e.g., random forest)
        prediction = "Home Win" if home_advantage * 0.9 > away_advantage else "Away Win" if home_advantage < away_advantage * 0.9 else "Draw"
    
    return prediction

# Helper functions for fetching recent form and goal averages
def get_recent_form(team_id):
    url = f'{BASE_URL}teams/{team_id}/matches?status=FINISHED&limit=5'
    response = requests.get(url, headers=headers)
    data = response.json()

    recent_points = 0
    for match in data.get('matches', []):
        if match['homeTeam']['id'] == team_id:
            recent_points += 3 if match['score']['winner'] == 'HOME_TEAM' else 1 if match['score']['winner'] == 'DRAW' else 0
        elif match['awayTeam']['id'] == team_id:
            recent_points += 3 if match['score']['winner'] == 'AWAY_TEAM' else 1 if match['score']['winner'] == 'DRAW' else 0
    return recent_points

def get_avg_goals(team_id):
    url = f'{BASE_URL}teams/{team_id}/matches?status=FINISHED&limit=5'
    response = requests.get(url, headers=headers)
    data = response.json()

    goals_scored = 0
    goals_conceded = 0
    matches = data.get('matches', [])
    
    for match in matches:
        if match['homeTeam']['id'] == team_id:
            goals_scored += match['score']['fullTime']['homeTeam']
            goals_conceded += match['score']['fullTime']['awayTeam']
        elif match['awayTeam']['id'] == team_id:
            goals_scored += match['score']['fullTime']['awayTeam']
            goals_conceded += match['score']['fullTime']['homeTeam']
    
    return (goals_scored / len(matches) if matches else 0,
            goals_conceded / len(matches) if matches else 0)

if __name__ == '__main__':
    app.run(debug=True)
