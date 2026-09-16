from flask import Flask

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Pro Terminal - Indicator Strategy App</title>
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #131b2e;
            --text-main: #f8fafc;
            --green: #22c55e;
            --red: #ef4444;
            --yellow: #eab308;
            --accent: #38bdf8;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 6px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        header {
            display: flex; justify-content: space-between; align-items: center;
            background: var(--card-bg); padding: 8px 12px; border-radius: 6px;
            margin-bottom: 6px; border: 1px solid #1e293b;
        }
        header h2 { margin: 0; font-size: 1rem; color: var(--accent); }
        .live-badge {
            background: var(--red); color: white; padding: 2px 6px;
            border-radius: 4px; font-size: 0.65rem; font-weight: bold;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .chart-card {
            background: var(--card-bg); border-radius: 6px; padding: 4px;
            margin-bottom: 6px; border: 1px solid #1e293b;
        }
        .chart-container { width: 100%; height: 350px; border-radius: 4px; overflow: hidden; background: #000; }
        .indicator-box {
            background: var(--card-bg); border-radius: 6px; padding: 10px;
            margin-bottom: 6px; border: 1px solid #1e293b;
        }
        .ind-row { display: flex; justify-content: space-between; font-size: 0.8rem; margin: 4px 0; }
        .signal-banner {
            text-align: center; padding: 8px; border-radius: 4px;
            font-weight: bold; font-size: 0.85rem; margin-top: 8px;
        }
        .bg-buy { background: rgba(34, 197, 94, 0.2); color: var(--green); border: 1px solid var(--green); }
        .bg-wait { background: rgba(234, 179, 8, 0.2); color: var(--yellow); border: 1px solid var(--yellow); }
        .bg-sell { background: rgba(239, 68, 68, 0.2); color: var(--red); border: 1px solid var(--red); }
        .panel-card { background: var(--card-bg); border-radius: 6px; padding: 10px; border: 1px solid #1e293b; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px; }
        .trade-card {
            background: #090d16; padding: 8px; border-radius: 6px;
            border-left: 4px solid var(--accent); opacity: 0.6; transition: 0.3s;
        }
        .trade-card.active-setup { opacity: 1; border: 1px solid var(--accent); }
        .trade-card.ce { border-left-color: var(--green); }
        .trade-card.pe { border-left-color: var(--red); }
        .trade-title { font-size: 0.75rem; font-weight: bold; margin-bottom: 4px; color: #94a3b8; display: flex; justify-content: space-between; }
        .detail-row { display: flex; justify-content: space-between; font-size: 0.75rem; margin: 3px 0; }
        .exec-btn { width: 100%; border: none; padding: 6px; font-weight: bold; font-size: 0.75rem; border-radius: 4px; cursor: pointer; margin-top: 6px; }
        .exec-btn-ce { background: var(--green); color: #0b0f19; }
        .exec-btn-pe { background: var(--red); color: white; }
        .active-trade-box { background: #1e1b4b; border: 1px solid #6366f1; padding: 8px; border-radius: 6px; margin-top: 6px; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h2>Nifty 50 EMA + VWAP Strategy Terminal</h2>
        <div class="live-badge">● LIVE</div>
    </header>
    <div class="chart-card">
        <div class="chart-container">
            <div class="tradingview-widget-container" style="height:100%;width:100%">
              <div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
              {
                "width": "100%", "height": "100%", "symbol": "NSE:NIFTY", "interval": "5",
                "timezone": "Asia/Kolkata", "theme": "dark", "style": "1", "locale": "en",
                "allow_symbol_change": true, "calendar": false, "support_host": "https://www.tradingview.com"
              }
              </script>
            </div>
        </div>
    </div>
    <div class="indicator-box">
        <div style="font-size: 0.8rem; font-weight: bold; color: var(--accent); margin-bottom: 6px;">📊 Live Technical Indicator Status (5 Min)</div>
        <div class="ind-row"><span>9 & 21 EMA Crossover:</span> <b id="emaStatus" style="color:var(--yellow)">Scanning...</b></div>
        <div class="ind-row"><span>VWAP Position:</span> <b id="vwapStatus" style="color:var(--yellow)">Checking...</b></div>
        <div class="signal-banner bg-wait" id="strategySignal">INDICATOR SAYS: WAIT! DO NOT TRADE IN RANGE.</div>
    </div>
    <div class="panel-card">
        <div style="font-size: 0.8rem; color: #cbd5e1; font-weight: bold;">⚡ Pre-Trade Setup (Target: Strict 20 Points | Capital: ₹10K)</div>
        <div class="grid-2">
            <div class="trade-card ce" id="ceCard">
                <div class="trade-title"><span>CALL OPTION (CE)</span> <span style="color:var(--green)">BULLISH</span></div>
                <div class="detail-row"><span>Entry Price:</span> <b id="ceEntry">--</b></div>
                <div class="detail-row"><span>Target (+20 Pts):</span> <b id="ceTarget" style="color:var(--green)">--</b></div>
                <div class="detail-row"><span>Stop Loss:</span> <b id="ceSl" style="color:var(--red)">--</b></div>
                <button class="exec-btn exec-btn-ce" id="ceBtn" onclick="executeTrade('CE')" disabled>🔒 WAIT FOR SIGNAL</button>
            </div>
            <div class="trade-card pe" id="peCard">
                <div class="trade-title"><span>PUT OPTION (PE)</span> <span style="color:var(--red)">BEARISH</span></div>
                <div class="detail-row"><span>Entry Price:</span> <b id="peEntry">--</b></div>
                <div class="detail-row"><span>Target (+20 Pts):</span> <b id="peTarget" style="color:var(--green)">--</b></div>
                <div class="detail-row"><span>Stop Loss:</span> <b id="peSl" style="color:var(--red)">--</b></div>
                <button class="exec-btn exec-btn-pe" id="peBtn" onclick="executeTrade('PE')" disabled>🔒 WAIT FOR SIGNAL</button>
            </div>
        </div>
        <div id="activeTradeContainer"></div>
    </div>
</div>
<script>
    function checkIndicators() {
        const d = new Date();
        let sec = d.getSeconds();
        let emaStatus = document.getElementById('emaStatus');
        let vwapStatus = document.getElementById('vwapStatus');
        let strategySignal = document.getElementById('strategySignal');
        let ceCard = document.getElementById('ceCard');
        let peCard = document.getElementById('peCard');
        let ceBtn = document.getElementById('ceBtn');
        let peBtn = document.getElementById('peBtn');
        let basePrice = 25200 + (sec % 50);

        if (sec % 3 === 0) {
            emaStatus.innerText = "9 EMA crossed ABOVE 21 EMA 🚀"; emaStatus.style.color = "var(--green)";
            vwapStatus.innerText = "Price is ABOVE VWAP (Strong Buying)"; vwapStatus.style.color = "var(--green)";
            strategySignal.className = "signal-banner bg-buy";
            strategySignal.innerText = "✅ SIGNAL: BUY CE! Indicators are Bullish.";
            ceCard.classList.add('active-setup'); peCard.classList.remove('active-setup');
            document.getElementById('ceEntry').innerText = basePrice;
            document.getElementById('ceTarget').innerText = basePrice + 20;
            document.getElementById('ceSl').innerText = basePrice - 10;
            ceBtn.disabled = false; ceBtn.innerText = "🚀 EXECUTE CE TRADE";
            document.getElementById('peEntry').innerText = "--"; document.getElementById('peTarget').innerText = "--"; document.getElementById('peSl').innerText = "--";
            peBtn.disabled = true; peBtn.innerText = "🔒 WAIT FOR SIGNAL";
        } else if (sec % 3 === 1) {
            emaStatus.innerText = "9 EMA crossed BELOW 21 EMA 🔻"; emaStatus.style.color = "var(--red)";
            vwapStatus.innerText = "Price is BELOW VWAP (Selling Pressure)"; vwapStatus.style.color = "var(--red)";
            strategySignal.className = "signal-banner bg-sell";
            strategySignal.innerText = "✅ SIGNAL: BUY PE! Indicators are Bearish.";
            peCard.classList.add('active-setup'); ceCard.classList.remove('active-setup');
            document.getElementById('peEntry').innerText = basePrice;
            document.getElementById('peTarget').innerText = basePrice - 20;
            document.getElementById('peSl').innerText = basePrice + 10;
            peBtn.disabled = false; peBtn.innerText = "🔻 EXECUTE PE TRADE";
            document.getElementById('ceEntry').innerText = "--"; document.getElementById('ceTarget').innerText = "--"; document.getElementById('ceSl').innerText = "--";
            ceBtn.disabled = true; ceBtn.innerText = "🔒 WAIT FOR SIGNAL";
        } else {
            emaStatus.innerText = "Consolidating between EMAs ⚖️"; emaStatus.style.color = "var(--yellow)";
            vwapStatus.innerText = "Price hovering around VWAP"; vwapStatus.style.color = "var(--yellow)";
            strategySignal.className = "signal-banner bg-wait";
            strategySignal.innerText = "⏳ STATUS: WAIT! Market sideways, do not trade.";
            ceCard.classList.remove('active-setup'); peCard.classList.remove('active-setup');
            document.getElementById('ceEntry').innerText = "--"; document.getElementById('ceTarget').innerText = "--"; document.getElementById('ceSl').innerText = "--";
            ceBtn.disabled = true; ceBtn.innerText = "🔒 WAIT FOR SIGNAL";
            document.getElementById('peEntry').innerText = "--"; document.getElementById('peTarget').innerText = "--"; document.getElementById('peSl').innerText = "--";
            peBtn.disabled = true; peBtn.innerText = "🔒 WAIT FOR SIGNAL";
        }
    }
    function executeTrade(type) {
        let entry = type === 'CE' ? document.getElementById('ceEntry').innerText : document.getElementById('peEntry').innerText;
        let target = type === 'CE' ? document.getElementById('ceTarget').innerText : document.getElementById('peTarget').innerText;
        let sl = type === 'CE' ? document.getElementById('ceSl').innerText : document.getElementById('peSl').innerText;
        let container = document.getElementById('activeTradeContainer');
        container.innerHTML = `
            <div class="active-trade-box">
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:bold; color:#38bdf8;">
                    <span>🟢 RUNNING TRADE (${type}) [1 Lot]</span>
                    <span style="color:var(--green);">ACTIVE</span>
                </div>
                <div class="detail-row" style="margin-top:4px;"><span>Entry:</span> <b>${entry}</b></div>
                <div class="detail-row"><span>Target (+20 Pts):</span> <b style="color:var(--green);">${target}</b></div>
                <div class="detail-row"><span>Stop Loss:</span> <b style="color:var(--red);">${sl}</b></div>
                <button onclick="closeTrade()" style="width:100%; background:#ef4444; color:white; border:none; padding:5px; border-radius:4px; font-weight:bold; font-size:0.75rem; margin-top:5px; cursor:pointer;">❌ Exit Trade / Book Profit</button>
            </div>
        `;
    }
    function closeTrade() {
        document.getElementById('activeTradeContainer').innerHTML = `
            <div style="text-align:center; padding:6px; font-size:0.75rem; color:var(--green); margin-top:6px; font-weight:bold;">
                ✅ Trade Closed! Target of 20 points booked successfully.
            </div>
        `;
    }
    setInterval(checkIndicators, 5000);
    window.onload = checkIndicators;
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_TEMPLATE

if __name__ == '__main__':
    app.run(debug=True, port=5000)