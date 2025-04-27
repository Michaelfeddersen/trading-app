import React, { useState, useEffect } from 'react';
import Chart from './components/Chart';
import Select from 'react-select';
import './index.css';

const LABELS = {
  0: "Double Bottom",
  1: "Double Top",
  2: "Rising Wedge",
  3: "Falling Wedge",
  4: "No Pattern"
};

const NASDAQ_100 = [
  { value: 'AAPL', label: 'Apple' },
  { value: 'TSLA', label: 'Tesla' },
  { value: 'NVDA', label: 'Nvidia' },
  { value: 'WMT', label: 'Walmart' },
];

// Mehr Timeframes!
const TIMEFRAMES = [
  { value: '1d', label: '1 Tag' },
  { value: '5d', label: '5 Tage' },
  { value: '1mo', label: '1 Monat' },
  { value: '3mo', label: '3 Monate' },
  { value: '6mo', label: '6 Monate' },
  { value: '1y', label: '1 Jahr' },
  { value: '5y', label: '5 Jahr' },
  { value: '10y', label: '10 Jahr' },
  { value: 'ytd', label: 'YTD' },
  { value: 'max', label: 'Max' },
];

function App() {
  const [stock, setStock] = useState(NASDAQ_100[0]);
  const [timeframe, setTimeframe] = useState(TIMEFRAMES[0]);
  const [chartData, setChartData] = useState([]);
  const [pattern, setPattern] = useState(null);
  const [patternSource, setPatternSource] = useState(null);
  const [highlight, setHighlight] = useState(null);
  const [marker, setMarker] = useState(null);

  const handleDetectPattern = async () => {
    const response = await fetch(`http://localhost:8000/detect/${stock.value}`);
    const result = await response.json();
    setPattern(result);
    setPatternSource('logic');  // 👈 Logik-Erkennung
    alert(`KI-Erkennung: ${result.pattern} (Confidence: ${result.confidence.toFixed(2)})`);
  };
  
  // NEU HINZUFÜGEN!
  const handleDetectRealPattern = async () => {
    try {
      const response = await fetch(`http://localhost:8000/detect_real/${stock.value}`);
      const result = await response.json();
  
      if (result && result.pattern && result.confidence > 0.4) {  // 👈 HIER!!!!!!!!!!!!!!!
        setPattern(result);
        setPatternSource('ai');
  
        setHighlight({
          from: new Date(result.start_date),
          to: new Date(result.end_date),
        });
  
        setMarker({
          time: Math.floor(new Date(result.end_date).getTime() / 1000),
          price: result.entry_point,
        });

        setPatternSource('ai');
            alert(`KI-Erkennung (Real): ${result.pattern} (Confidence: ${result.confidence.toFixed(2)})`);
    } else {
      alert("🚫 Keine zuverlässige Mustererkennung! (Confidence zu niedrig unter 0.6)");
    }
  } catch (error) {
    console.error("Fehler bei detect_real_pattern:", error);
    alert("Fehler bei der Mustererkennung 🚫");
  }
};
  
  
  

  useEffect(() => {
    fetch(`http://localhost:8000/stock/${stock.value}?interval=${timeframe.value}`)
      .then((res) => res.json())
      .then((data) => {
        const formattedData = data
          .filter(d => d.Date && d.Close != null)
          .map(d => ({
            time: Math.floor(new Date(d.Date).getTime() / 1000),
            open: d.Open,
            high: d.High,
            low: d.Low,
            close: d.Close,
            volume: d.Volume,
            sma: d.SMA_14 ?? null,
            ema14: d.EMA_14 ?? null,
            ema50: d.EMA_50 ?? null,
            rsi: d.RSI_14 ?? null,
            bollingerUpper: d.Bollinger_Upper ?? null,
            bollingerLower: d.Bollinger_Lower ?? null,
            macd: d.MACD ?? null,
            macdSignal: d.MACD_Signal ?? null,
          }))
          .filter(d => !isNaN(d.time))
          .sort((a, b) => a.time - b.time);

        setChartData(formattedData);
      })
      .catch(error => console.error("Fehler beim Laden der Stock-Daten:", error));
  }, [stock, timeframe]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 sm:p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl sm:text-4xl font-bold mb-6 text-center">📈 KI-Börsenanalyse</h1>

        {/* Auswahl: Aktie + Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
          <div className="w-full sm:w-1/2">
            <Select
              options={NASDAQ_100}
              value={stock}
              onChange={setStock}
              className="text-black z-50"
              classNamePrefix="react-select"
            />
          </div>

          <button
            onClick={handleDetectPattern}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-all"
          >
            Muster erkennen
          </button>
          <button
  onClick={handleDetectRealPattern}
  className="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded transition-all"
>
  Echte Muster erkennen
</button>
          
        </div>

        {/* Timeframe-Buttons */}
        <div className="flex flex-wrap justify-center gap-2 mb-6">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-2 rounded text-sm font-medium transition-all ${
                timeframe.value === tf.value ? 'bg-blue-600 text-white' : 'bg-gray-600 text-gray-300'
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>

        {/* Chart */}
        <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
        <Chart data={chartData} patternPoint={marker} />
        </div>

        {/* Ergebnis */}
        {pattern && (
  <div className={`p-6 rounded-lg shadow-lg mt-8 text-center ${patternSource === 'ai' ? 'bg-blue-800' : 'bg-green-800'}`}>
    <h2 className="text-2xl font-bold mb-4">
      {patternSource === 'ai' ? '🤖' : '✅'} KI-Analyse-Ergebnis
    </h2>
    
    <p className="mb-2">📊 Muster: <strong>{pattern.pattern}</strong></p>

    <p className="mb-2">🤖 Vertrauen: <strong>{pattern.confidence.toFixed(2)}</strong></p>
    <p>🎯 Einstiegspunkt: <strong>{pattern.entry_point.toFixed(2)} $</strong></p>
  </div>
)}
      </div>
    </div>
  );
}

export default App;
