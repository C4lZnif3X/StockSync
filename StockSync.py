from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

def format_compact(val):
    try:
        val = float(val)
        if val >= 1e12:
            return f"{val/1e12:.1f}T"
        elif val >= 1e9:
            return f"{val/1e9:.1f}B"
        elif val >= 1e6:
            return f"{val/1e6:.1f}M"
        elif val >= 1e3:
            return f"{val/1e3:.1f}K"
        else:
            return f"{val:.2f}"
    except:
        return "N/A"

@app.route("/fetch")
def fetch_stock_data():
    try:
        ticker = request.args.get("ticker", "").upper()
        if not ticker:
            return jsonify({"error": "Missing ticker"}), 400

        stock = yf.Ticker(ticker)
        info = stock.info

        # Operating income fallback
        operating_income = (
            info.get("operatingIncome")
            or info.get("totalOperatingIncome")
            or info.get("operatingIncomeLoss")
            or "N/A"
        )
        if operating_income in [None, 0, "N/A", "-N/A"]:
            try:
                fin = stock.financials
                if "Operating Income" in fin.index:
                    fallback_val = fin.loc["Operating Income"].iloc[0]
                    operating_income = fallback_val if fallback_val != 0 else "N/A"
            except Exception as e:
                print("Fallback financials error:", e)

        # Format everything consistently
                data = {
            "ticker": ticker,
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "price": format_compact(info.get("currentPrice")),
            "fiftyTwoWeekHigh": format_compact(info.get("fiftyTwoWeekHigh")),
            "fiftyTwoWeekLow": format_compact(info.get("fiftyTwoWeekLow")),
            "marketCap": format_compact(info.get("marketCap")),
            "revenue": format_compact(info.get("totalRevenue") or info.get("totalRevenueTTM")),
            "netIncome": format_compact(info.get("netIncomeToCommon") or info.get("netIncome")),
            "freeCashFlow": format_compact(info.get("freeCashflow") or info.get("operatingCashflow")),
            "dividendYield": (
                f"{float(info.get('dividendYield', 0)) * 100:.2f}%" if info.get("dividendYield") else "N/A"
            ),
            "dividendPerShare": format_compact(info.get("dividendRate")),
            "PEratio": format_compact(
                info.get("trailingPE") or
                info.get("priceToEarnings") or
                "N/A"
            ),
            "forwardPE": format_compact(info.get("forwardPE") or "N/A"),
            "DebtToEquity": format_compact(info.get("debtToEquity") or "N/A"),
            "operatingIncome": format_compact(operating_income)
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
