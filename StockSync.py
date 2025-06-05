from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from Google Sheets or any frontend

@app.route('/fetch', methods=['GET', 'POST'])
def fetch_stock_data():
    ticker = request.args.get('ticker') or (request.json.get('ticker') if request.is_json else None)
    print(f"→ RECEIVED TICKER: {ticker}")  # Debug: log what we get

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            "ticker": ticker.upper(),
            "name": info.get("shortName"),
            "sector": info.get("sector"),
            "marketCap": info.get("marketCap"),
            "price": info.get("regularMarketPrice"),
            "peRatio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "dividendYield": info.get("dividendYield"),
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
