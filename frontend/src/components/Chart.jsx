import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import { calculateMACDSignals } from '../utils/tradingSignals';

function Chart({ data, patternPoint = null }) {
  const chartContainerRef = useRef();
  const macdContainerRef = useRef();
  const [chartInstance, setChartInstance] = useState(null);
  const [series, setSeries] = useState({});
  const [showMACD, setShowMACD] = useState(true);
  const [showCandles, setShowCandles] = useState(true);
  const [showSMA, setShowSMA] = useState(true);
  const [showEMA14, setShowEMA14] = useState(false);
  const [showEMA50, setShowEMA50] = useState(false);
  const [showBollinger, setShowBollinger] = useState(false);
  const [showRSI, setShowRSI] = useState(false);
  const [infoText, setInfoText] = useState('');

  const handleInfo = (type) => {
    switch (type) {
      case 'sma':
        setInfoText('SMA 14: Einfacher gleitender Durchschnitt der letzten 14 Tage.');
        break;
      case 'ema14':
        setInfoText('EMA 14: Exponentiell gewichteter Durchschnitt – legt mehr Gewicht auf neue Kurse.');
        break;
      case 'ema50':
        setInfoText('EMA 50: Längerfristiger Durchschnitt über 50 Tage.');
        break;
      case 'bollinger':
        setInfoText('Bollinger Bänder: Volatilität basierend auf Standardabweichung.');
        break;
      case 'rsi':
        setInfoText('RSI 14: Relative Stärke Index.');
        break;
      case 'kurs':
        setInfoText('Kerzenchart (Open, High, Low, Close).');
        break;
      default:
        setInfoText('');
    }
  };
  
  
  useEffect(() => {
    if (!data || data.length === 0) return;

    
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: { background: { color: "#1f2937" }, textColor: "#ffffff" },
      grid: { vertLines: { color: "#2d3748" }, horzLines: { color: "#2d3748" } },
      timeScale: { borderColor: "#485c7b" },
      priceScale: { borderColor: "#485c7b" },
    });

    const newSeries = {};

    // Kerzen
    if (showCandles) {
      newSeries.candles = chart.addCandlestickSeries();
      newSeries.candles.setData(data.map(d => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      })));

const signals = calculateMACDSignals(data);

newSeries.candles.setMarkers(
  signals.map(signal => ({
    time: signal.time,
    position: signal.type === 'BUY' ? 'belowBar' : 'aboveBar',
    color: signal.type === 'BUY' ? 'green' : 'red',
    shape: signal.type === 'BUY' ? 'arrowUp' : 'arrowDown',
    text: `${signal.type} @${signal.price.toFixed(2)}`,
  }))
);


    }

    // SMA
    if (showSMA) {
      newSeries.sma = chart.addLineSeries({ color: "blue", lineWidth: 2 });
      newSeries.sma.setData(data.filter(d => d.sma != null).map(d => ({
        time: d.time,
        value: d.sma,
      })));
    }

    // EMA14
    if (showEMA14) {
      newSeries.ema14 = chart.addLineSeries({ color: "orange", lineWidth: 2 });
      newSeries.ema14.setData(data.filter(d => d.ema14 != null).map(d => ({
        time: d.time,
        value: d.ema14,
      })));
    }

    // EMA50
    if (showEMA50) {
      newSeries.ema50 = chart.addLineSeries({ color: "red", lineWidth: 2 });
      newSeries.ema50.setData(data.filter(d => d.ema50 != null).map(d => ({
        time: d.time,
        value: d.ema50,
      })));
    }

    // Bollinger Bänder
    if (showBollinger) {
      newSeries.bollUpper = chart.addLineSeries({ color: "#d3d3d3", lineWidth: 1 });
      newSeries.bollLower = chart.addLineSeries({ color: "#d3d3d3", lineWidth: 1 });
      newSeries.bollUpper.setData(data.filter(d => d.bollingerUpper != null).map(d => ({
        time: d.time,
        value: d.bollingerUpper,
      })));
      newSeries.bollLower.setData(data.filter(d => d.bollingerLower != null).map(d => ({
        time: d.time,
        value: d.bollingerLower,
      })));
    }

    // RSI auf Hauptchart (optional)
    if (showRSI) {
      newSeries.rsi = chart.addLineSeries({ color: "purple", lineWidth: 2 });
      newSeries.rsi.setData(data.filter(d => d.rsi != null).map(d => ({
        time: d.time,
        value: d.rsi,
      })));
    }

    // Pattern-Point Marker
    if (patternPoint && newSeries.candles) {
      const newMarkers = [
        {
          time: patternPoint.time,
          position: 'belowBar',
          color: 'lime',    // Startfarbe
          shape: 'circle',
          text: 'Muster erkannt!',
        },
      ];
      newSeries.candles.setMarkers(newMarkers);
      
    
      chart.timeScale().setVisibleRange({
        from: patternPoint.time - 60 * 60 * 24 * 30,
        to: patternPoint.time + 60 * 60 * 24 * 10,
      });
    
      // ✨ Animation starten
      setTimeout(() => {
        const flashMarkers = newMarkers.map(m => ({ ...m, color: 'white' }));
        newSeries.candles.setMarkers(flashMarkers);
    
        setTimeout(() => {
          newSeries.candles.setMarkers(newMarkers); // Zurück zur Originalfarbe
        }, 400);
      }, 300);
    }

    setChartInstance(chart);
    setSeries(newSeries);

    return () => {
      chart.remove();
    }
    ;
  }, [data, showCandles, showSMA, showEMA14, showEMA50, showBollinger, showRSI, patternPoint]);
  useEffect(() => {
    if (!data || data.length === 0 || !showMACD) return;

    const macdChart = createChart(macdContainerRef.current, {
      width: macdContainerRef.current.clientWidth,
      height: 200,
      layout: { background: { color: "#1f2937" }, textColor: "#ffffff" },
      grid: { vertLines: { color: "#2d3748" }, horzLines: { color: "#2d3748" } },
      timeScale: { borderColor: "#485c7b" },
      priceScale: { borderColor: "#485c7b" },
    });

    const macdLine = macdChart.addLineSeries({ color: "cyan", lineWidth: 2 });
    const signalLine = macdChart.addLineSeries({ color: "magenta", lineWidth: 2 });

    macdLine.setData(data.filter(d => d.macd != null).map(d => ({ time: d.time, value: d.macd })));
    signalLine.setData(data.filter(d => d.macdSignal != null).map(d => ({ time: d.time, value: d.macdSignal })));

    const histogram = macdChart.addHistogramSeries({
      color: "green",
      lineWidth: 1,
      priceFormat: { type: "volume" },
      base: 0,
    });

    histogram.setData(
      data.map(d => {
        if (d.macd != null && d.macdSignal != null) {
          return {
            time: d.time,
            value: d.macd - d.macdSignal,
            color: (d.macd - d.macdSignal) >= 0 ? 'rgba(0,255,0,0.7)' : 'rgba(255,0,0,0.7)'
          };
        }
        return { time: d.time, value: 0 };
      })
    );

    return () => macdChart.remove();
  }, [data, showMACD]);
  return (
    <div className="w-full flex flex-col items-center">

      {/* Buttons */}
      <div className="flex flex-wrap justify-center gap-3 mb-6">
        <button
          className={`px-4 py-2 rounded ${showCandles ? "bg-green-600" : "bg-gray-600"}`}
          onClick={() => { setShowCandles(!showCandles); handleInfo('kurs'); }}
        >Kurs</button>

        <button
          className={`px-4 py-2 rounded ${showSMA ? "bg-blue-600" : "bg-gray-600"}`}
          onClick={() => { setShowSMA(!showSMA); handleInfo('sma'); }}
        >SMA 14</button>

        <button
          className={`px-4 py-2 rounded ${showEMA14 ? "bg-yellow-500" : "bg-gray-600"}`}
          onClick={() => { setShowEMA14(!showEMA14); handleInfo('ema14'); }}
        >EMA 14</button>

        <button
          className={`px-4 py-2 rounded ${showEMA50 ? "bg-red-600" : "bg-gray-600"}`}
          onClick={() => { setShowEMA50(!showEMA50); handleInfo('ema50'); }}
        >EMA 50</button>

        <button
          className={`px-4 py-2 rounded ${showBollinger ? "bg-gray-400" : "bg-gray-600"}`}
          onClick={() => { setShowBollinger(!showBollinger); handleInfo('bollinger'); }}
        >Bollinger</button>

        <button
          className={`px-4 py-2 rounded ${showRSI ? "bg-purple-600" : "bg-gray-600"}`}
          onClick={() => { setShowRSI(!showRSI); handleInfo('rsi'); }}
        >RSI 14</button>
      </div>

      {infoText && (
        <div className="mt-4 text-center text-sm text-gray-300">
          {infoText}
        </div>
      )}

      {/* Chart */}
      <div ref={chartContainerRef} className="w-full max-w-5xl h-[400px] border rounded-lg shadow-lg mb-8" />

      {/* MACD Chart unten */}
      {showMACD && (
        <div className="w-full max-w-5xl">
          <div className="text-center mb-2">
            <h2 className="text-lg font-bold text-white">MACD</h2>
            <p className="text-gray-400 text-sm">Moving Average Convergence Divergence.</p>
          </div>
          <div ref={macdContainerRef} className="w-full h-[200px] border rounded-lg shadow-lg" />
        </div>
      )}
    </div>
  );
}

export default Chart;
