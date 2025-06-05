from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/fetch')
def fetch_stock_data():
    try:
        ticker = request.args.get('ticker', '').upper()
        if not ticker:
            return jsonify({'error': 'Missing ticker'}), 400

        stock = yf.Ticker(ticker)
        info = stock.info

        # Fallback for Operating Income
        operating_income = (
            info.get('operatingIncome') or
            info.get('totalOperatingIncome') or
            info.get('operatingIncomeLoss') or
            info.get('OperatingIncome') or
            info.get('OperatingIncomeLoss') or
            info.get('OperatingIncomeLossFromContinuingOperations') or
            "N/A"
        )

        # Fallback for PE Ratio
        pe_ratio = (
            info.get('trailingPE') or
            info.get('forwardPE') or
            info.get('priceToEarningsRatio') or
            info.get('PERatio') or
            "N/A"
        )

        data = {
            'ticker': ticker,
            'name': info.get('longName', "N/A"),
            'sector': info.get('sector', "N/A"),
            'price': info.get('currentPrice', "N/A"),
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', "N/A"),
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', "N/A"),
            'marketCap': info.get('marketCap', "N/A"),
            'revenue': info.get('totalRevenue', "N/A"),
            'netIncome': info.get('netIncomeToCommon', "N/A"),
            'freeCashFlow': info.get('freeCashflow', "N/A"),
            'dividendYield': info.get('dividendYield', "N/A"),
            'dividendPerShare': info.get('dividendRate', "N/A"),
            'pERatio': pe_ratio,
            'forwardPE': info.get('forwardPE', "N/A"),
            'debtToEquity': info.get('debtToEquity', "N/A"),
            'operatingIncome': operating_income
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
