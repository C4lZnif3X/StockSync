from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Google Sheets or anywhere

@app.route('/fetch')
def fetch_stock_data():
    try:
        ticker = request.args.get('ticker', '').upper()
        if not ticker:
            return jsonify({'error': 'Missing ticker'}), 400

        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            'ticker': ticker,
            'name': info.get('longName'),
            'sector': info.get('sector'),
            'price': info.get('currentPrice'),
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow'),
            'marketCap': info.get('marketCap'),
            'revenue': info.get('totalRevenue'),
            'netIncome': info.get('netIncomeToCommon'),
            'freeCashFlow': info.get('freeCashflow'),
            'dividendYield': info.get('dividendYield'),
            'dividendPerShare': info.get('dividendRate'),
            'peRatio': info.get('trailingPE'),
            'forwardPE': info.get('forwardPE'),
            'debtToEquity': info.get('debtToEquity'),
            'operatingIncome': info.get('operatingIncome'),
            'ebitda': info.get('ebitda')
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
