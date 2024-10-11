from flask import Flask, request, render_template
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)


teams = ['Team A', 'Team B', 'Team C', 'Team D']


logreg = LogisticRegression()
rf = RandomForestClassifier()


dummy_X_train = pd.DataFrame({
    'home_team': [0, 1, 2, 3],
    'away_team': [1, 0, 3, 2]
})
dummy_y_train = [1, -1, 0, 1]

logreg.fit(dummy_X_train, dummy_y_train)
rf.fit(dummy_X_train, dummy_y_train)

team_encoder = {team: i for i, team in enumerate(teams)}

@app.route('/')
def home():
    return render_template('index.html', teams=teams)

@app.route('/predict', methods=['POST'])
def predict():
    home_team = request.form['home_team']
    away_team = request.form['away_team']

    home_team_encoded = team_encoder[home_team]
    away_team_encoded = team_encoder[away_team]

    features = pd.DataFrame([[home_team_encoded, away_team_encoded]], columns=['home_team', 'away_team'])

    logreg_prediction = logreg.predict(features)[0]
    rf_prediction = rf.predict(features)[0]

    result_map = {1: "Home Win", 0: "Draw", -1: "Away Win"}

    return render_template('result.html',
                           home_team=home_team,
                           away_team=away_team,
                           logreg_result=result_map[logreg_prediction],
                           rf_result=result_map[rf_prediction])

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
