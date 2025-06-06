from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

def format_compact(val):
    try:
        if val is None or val == "N/A":
            return "-"
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
    except:
        return "-"

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
            info.get("operatingIncome") or
            info.get("totalOperatingIncome") or
            info.get("operatingIncomeLoss") or
            "-"
        )

        if operating_income in [None, 0, "-", "-N/A"]:
            try:
                fin = stock.financials
                if "Operating Income" in fin.index:
                    fallback_val = fin.loc["Operating Income"].iloc[0]
                    operating_income = fallback_val if fallback_val != 0 else "-"
            except Exception as e:
                print("Fallback financials error:", e)

        # Handle dividend yield safely
        try:
            dyield = info.get("dividendYield")
            dividend_yield = f"{float(dyield) * 100:.2f}%" if dyield else "-"
        except:
            dividend_yield = "-"

        data = {
            "ticker": ticker,
            "name": info.get("longName", "-"),
            "sector": info.get("sector", "-"),
            "price": format_compact(info.get("currentPrice")),
            "fiftyTwoWeekHigh": format_compact(info.get("fiftyTwoWeekHigh")),
            "fiftyTwoWeekLow": format_compact(info.get("fiftyTwoWeekLow")),
            "marketCap": format_compact(info.get("marketCap")),
            "revenue": format_compact(info.get("totalRevenue") or info.get("totalRevenueTTM")),
            "netIncome": format_compact(info.get("netIncomeToCommon") or info.get("netIncome")),
            "freeCashFlow": format_compact(info.get("freeCashflow") or info.get("operatingCashflow")),
            "dividendYield": dividend_yield,
            "dividendPerShare": format_compact(info.get("dividendRate")),
            "PEratio": format_compact(
                info.get("trailingPE") or info.get("priceToEarnings") or "-"
            ),
            "forwardPE": format_compact(info.get("forwardPE") or "-"),
            "DebtToEquity": format_compact(info.get("debtToEquity") or "-"),
            "operatingIncome": format_compact(operating_income or "-")
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
