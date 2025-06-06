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
            "N/A"
        )

        if operating_income in [None, 0, "N/A", "-N/A"]:
            try:
                fin = stock.financials
                if "Operating Income" in fin.index:
                    fallback_val = fin.loc["Operating Income"].iloc[0]
                    operating_income = fallback_val if fallback_val != 0 else "N/A"
            except Exception as e:
                print("Fallback financials error:", e)

        # ✅ THIS IS WHERE WE DEFINE `data`
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
                info.get("trailingPE") or info.get("priceToEarnings") or "N/A"
            ),
            "forwardPE": format_compact(info.get("forwardPE") or "N/A"),
            "DebtToEquity": format_compact(info.get("debtToEquity") or "N/A"),
            "operatingIncome": format_compact(operating_income)
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
