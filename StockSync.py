from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

def format_compact(val):
    try:
        if val is None or val == "N/A":
            return "-"
        val = float(val)
        if abs(val) >= 1_000_000_000_000:
            return f"{val / 1_000_000_000_000:.1f}T"
        elif abs(val) >= 1_000_000_000:
            return f"{val / 1_000_000_000:.1f}B"
        elif abs(val) >= 1_000_000:
            return f"{val / 1_000_000:.1f}M"
        elif abs(val) >= 1_000:
            return f"{val / 1_000:.1f}K"
        else:
            return f"{val:.2f}"
    except Exception:
        return "-"

@app.route("/fetch")
def fetch_stock_data():
    try:
        ticker = request.args.get("ticker", "").upper().strip()
        if not ticker or ticker in {"TICKER", "NONE", "UNDEFINED"}:
            return jsonify({"error": "Missing or invalid ticker"}), 400

        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or "longName" not in info:
            return jsonify({"error": f"No data for ticker: {ticker}"}), 404

        # Fallback hunt for operating income
        operating_income = (
            info.get("operatingIncome") or
            info.get("totalOperatingIncome") or
            info.get("operatingIncomeLoss") or
            "-"
        )
        if operating_income in [None, 0, "N/A", "-", ""]:
            try:
                fin = stock.financials
                if "Operating Income" in fin.index:
                    val = fin.loc["Operating Income"].iloc[0]
                    if val and val != 0:
                        operating_income = val
            except Exception:
                pass

        data = {
            "ticker": ticker,
            "name": info.get("longName", "-"),
            "sector": info.get("sector", "-"),
            "price": format_compact(info.get("currentPrice")),
            "fiftyTwoWeekHigh": format_compact(info.get("fiftyTwoWeekHigh")),
            "fiftyTwoWeekLow": format_compact(info.get("fiftyTwoWeekLow")),
            "marketCap": format_compact(info.get("marketCap")),
            "revenue": format_compact(info.get("totalRevenue")),
            "netIncome": format_compact(info.get("netIncomeToCommon") or info.get("netIncome")),
            "freeCashFlow": format_compact(info.get("freeCashflow")),
            "dividendYield": f'{float(info["dividendYield"]) * 100:.2f}%' if info.get("dividendYield") else "-",
            "dividendPerShare": format_compact(info.get("dividendRate")),
            "peRatio": format_compact(info.get("trailingPE") or info.get("priceToEarnings")),
            "forwardPE": format_compact(info.get("forwardPE")),
            "debtToEquity": format_compact(info.get("debtToEquity")),
            "operatingIncome": format_compact(operating_income),
            "sharesOutstanding": format_compact(info.get("sharesOutstanding")),
            "eps": format_compact(info.get("trailingEps") or info.get("epsForward")),
        }

        return jsonify(data)

    except Exception as e:
        print(f"[❌ ERROR] {ticker} → {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
