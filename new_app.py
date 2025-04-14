from flask import Flask, request, redirect, url_for, render_template
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)

model = joblib.load('models/fund_performance_classifier.pk1')
data = pd.read_csv('data/My new Raw Dataset.csv')
data.dropna(inplace=True)

data['Fund House'] = data['Fund House'].astype(str).str.strip()
data['Fund Type'] = data['Fund Type'].astype(str).str.strip()

inverse_label_map = {
    0:'Average',
    1:'Excellent',
    2:'Good',
    3:'Under Performed'
}

performance_score_map = {
    'Excellent':4,
    'Good':3,
    'Average':2,
    'Under Performed':1
}

weight_pref = 0.6
weight_return = 0.4

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/input')
def input_form():
    fund_house = sorted (data['Fund House'].unique())
    fund_type = sorted(data['Fund Type'].unique())
    return render_template('input.html', fund_house=fund_house, fund_type=fund_type)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        fund_house = request.form['fund_house']
        fund_type = request.form['fund_type']
        years = int(request.form['years'])
        invested_type = request.form['investment_type']

        if invested_type == 'SIP':
            min_sip = float(request.form['min_sip'])
            min_LumpSum = 0
        else:
            min_LumpSum = float(request.form['min_LumpSum'])
            min_sip = 0

        print("User Inputs:", fund_house, fund_type, years, min_sip, min_LumpSum)
        print("Available columns:", data.columns.tolist())

        mask = (
            (data['Fund House'] == fund_house) &
            (data['Fund Type'] == fund_type) &
            (data['Minimum SIP'] <= min_sip if invested_type == 'SIP' else True) &
            (data['Min_LumpSum'] <= min_LumpSum if invested_type == 'LumpSum' else True)
        )
        filtered = data[mask].copy()
        print("Filtered rows:", len(filtered))

        if filtered.empty:
            return render_template('home.html', results=[], message="No matching funds found.", fund_house=sorted(data['Fund House'].unique()), fund_type=sorted(data['Fund Type'].unique()))

        recommendations = []

        for _, row in filtered.iterrows():
            features = [row['NAV'], row['AUM'], row['Sharpe Ratio'], row['Alpha '], row['Beta']]
            pred_class = model.predict([features])[0]
            performance = inverse_label_map[pred_class]
            pref_score = performance_score_map[performance]

            if years == 1:
                returns = float(row['Returns (1Yr)'])
            elif years == 3:
                returns = float(row['Returns (3Yr)'])
            elif years == 5:
                returns = float(row['Returns (5Yr)'])
            else:
                returns = 0.0
            
            if invested_type == 'SIP':
                daily_rate = (1 + returns/100) ** (1/365) - 1
                days = years * 365
                future_value_SIP = sum([min_sip * ((1 + daily_rate) ** (days - d)) for d in range(1, days + 1)])
                return_amount = round(future_value_SIP, 2)
            else:
                return_amount = round(min_LumpSum * ((1 + returns / 100) ** years), 2)
            
            normalized_return = returns / 50 if returns is not None else 0

            custom_score = int(round((pref_score * weight_pref) + (normalized_return * weight_return), 2))

            recommendations.append({
                'Fund House': row['Fund House'],
                'Fund Name': row['Funds'],
                'Fund Type': row['Fund Type'],
                'NAV': row['NAV'],
                'AUM': row['AUM'],
                'Alpha': row['Alpha '],
                'Beta': row['Beta'],
                'Sharpe Ratio': row['Sharpe Ratio'],
                'Returns': returns,
                'Fund Performance': performance,
                'Expected Return Amount': return_amount,
                'Custom Score': custom_score
            })

            recommendations.sort(key=lambda x : x['Custom Score'], reverse=True)

        return render_template('results.html', results=recommendations, fund_house=sorted(data['Fund House'].unique()), fund_type=sorted(data['Fund Type'].unique()))
    
    except Exception as e:
        return f"<h3>Error Occurred:</h3><p>{str(e)}</p>"
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        return redirect(url_for('thank_you'))
    return render_template('signup.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')
   
if __name__=='__main__':
    app.run(debug=True)
