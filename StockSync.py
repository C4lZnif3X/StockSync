from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

def format_compact(val):
    if not val or val == "N/A" or val == "-N/A": return "N/A"
    abs_val = abs(val)
    if abs_val >= 1e12:
        return f"{val / 1e12:.1f}T"
    elif abs_val >= 1e9:
        return f"{val / 1e9:.1f}B"
    elif abs_val >= 1e6:
        return f"{val / 1e6:.1f}M"
    return str(val)

@app.route("/fetch")
def fetch_stock_data():
    try:
        ticker = request.args.get("ticker", "").upper()
        if not ticker:
            return jsonify({"error": "Missing ticker"}), 400

        stock = yf.Ticker(ticker)
        info = stock.info

        # Fallback logic for operating income
        operating_income = (
            info.get("operatingIncome")
            or info.get("totalOperatingIncome")
            or info.get("operatingIncomeLoss")
            or "-N/A"
        )

        # Try to grab from .financials dataframe if not in .info
        if operating_income == "-N/A":
            try:
                fin = stock.financials
                if "Operating Income" in fin.index:
                    operating_income = fin.loc["Operating Income"].iloc[0]
            except Exception as e:
                print("Fallback financials error:", e)

        data = {
            "ticker": ticker,
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "price": info.get("currentPrice", "N/A"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", "N/A"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", "N/A"),
            "marketCap": format_compact(info.get("marketCap")),
            "revenue": format_compact(info.get("totalRevenue")),
            "netIncome": format_compact(info.get("netIncomeToCommon")),
            "freeCashFlow": format_compact(info.get("freeCashflow")),
            "dividendYield": info.get("dividendYield", "N/A"),
            "dividendPerShare": info.get("dividendRate", "N/A"),
            "PEratio": info.get("trailingPE", "N/A"),
            "forwardPE": info.get("forwardPE", "N/A"),
            "debtToEquity": info.get("debtToEquity", "N/A"),
            "operatingIncome": format_compact(operating_income)
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
