// src/utils/tradingSignals.js

export function calculateMACDSignals(data) {
    const signals = [];
  
    for (let i = 1; i < data.length; i++) {
      const prev = data[i - 1];
      const curr = data[i];
  
      if (prev.macd != null && prev.macdSignal != null && curr.macd != null && curr.macdSignal != null) {
        if (prev.macd < prev.macdSignal && curr.macd > curr.macdSignal) {
          signals.push({ time: curr.time, type: 'BUY', price: curr.close });
        }
        if (prev.macd > prev.macdSignal && curr.macd < curr.macdSignal) {
          signals.push({ time: curr.time, type: 'SELL', price: curr.close });
        }
      }
    }
  
    return signals;
  }
  
  export function calculateRSISignals(data) {
    const signals = [];
  
    for (const d of data) {
      if (d.rsi != null) {
        if (d.rsi < 30) {
          signals.push({ time: d.time, type: 'BUY', price: d.close });
        }
        if (d.rsi > 70) {
          signals.push({ time: d.time, type: 'SELL', price: d.close });
        }
      }
    }
  
    return signals;
  }
  