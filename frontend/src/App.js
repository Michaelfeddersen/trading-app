import React, { useState, useEffect } from 'react';
import { createChart } from 'lightweight-charts';
import Select from 'react-select';

const NASDAQ_100 = [
  { value: 'AAPL', label: 'Apple' },
  { value: 'TSLA', label: 'Tesla' },
  { value: 'NVDA', label: 'Nvidia' },
  // ... mehr Ticker hinzufügen
];

function App() {
  const [stock, setStock] = useState(NASDAQ_100[0]);
  const [chart, setChart] = useState(null);
  const [pattern, setPattern] = useState(null);

  const handleDetectPattern = async () => {
    const response = await fetch(`http://localhost:8000/detect/${stock.value}`);
    const result = await response.json();
    setPattern(result);
    alert(`KI-Erkennung: ${result.pattern} (Confidence: ${result.confidence.toFixed(2)})`);
  };

  useEffect(() => {
    // Chart initialisieren
    const chart = createChart(document.getElementById('chart'), { 
      width: 800,
      height: 500,
    });
    const candleSeries = chart.addCandlestickSeries();
    setChart(candleSeries);

    return () => chart.remove();  // Cleanup
  }, []);

  useEffect(() => {
    if (!chart) return;

    // Daten vom Backend holen
    fetch(`http://localhost:8000/stock/${stock.value}`)
      .then(res => res.json())
      .then(data => {
        const formattedData = data.map(d => ({
          time: new Date(d.Date).getTime() / 1000,
          open: d.Open,
          high: d.High,
          low: d.Low,
          close: d.Close,
        }));
        chart.setData(formattedData);
      });
  }, [stock, chart]);

  return (
    <div style={{ padding: '20px' }}>
      <Select options={NASDAQ_100} value={stock} onChange={setStock} />
      <button onClick={handleDetectPattern}>Muster erkennen</button>
      <div id="chart" />
      {pattern && (
        <div>
          <h3>KI-Analyse:</h3>
          <p>Muster: {pattern.pattern}</p>
          <p>Confidence: {pattern.confidence.toFixed(2)}</p>
          <p>Möglicher Einstieg: ${pattern.entry_point.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
}

export default App;