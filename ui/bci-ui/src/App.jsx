// App.jsx
import { useState, useEffect } from 'react';
import './App.css';

const keyGrid = [
  ['Clr', 'L', 'Del'],
  ['F', 'T', 'J'],
  ['Q', 'V', 'M', 'I', 'O', 'K', '.'],
  [',', 'U', 'A', 'N', 'E', 'S', 'D', 'C'],
  ['G', 'P', 'W', 'R', 'B', 'Y', '-'],
  ['X', 'H', 'Z', 'Space']
];

const getClosestColumn = (targetCol, row) => {
  let closest = 0;
  let minDiff = Infinity;
  for (let i = 0; i < row.length; i++) {
    const diff = Math.abs(i - targetCol);
    if (diff < minDiff) {
      closest = i;
      minDiff = diff;
    }
  }
  return closest;
};

export default function App() {
  const [input, setInput] = useState('');
  const [predictions, setPredictions] = useState(["", "", ""]);
  const [cursor, setCursor] = useState({ row: 3, col: 4 }); // Start at 'E'

  useEffect(() => {
    const fetchPrediction = async () => {
      const trimmed = input.trim();
      if (!trimmed) {
        setPredictions(["", "", ""]);
        return;
      }

      const last = trimmed.split(" ").pop();
      const isPartial = /^[a-zA-Z]+$/.test(last);

      const endpoint = isPartial ? "predict_complete" : "predict_next";

      try {
        const res = await fetch(`http://localhost:8000/${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ input }),
        });
        const data = await res.json();
        setPredictions(data.predictions || ["", "", ""]);
      } catch (err) {
        console.error('Prediction error:', err);
        setPredictions(["", "", ""]);
      }
    };

    fetchPrediction();
  }, [input]);

  const handleMove = (dir) => {
    setCursor((prev) => {
      let { row, col } = prev;

      if (row === -1) {
        if (dir === 'down') return { row: 0, col: 1 };
        if (dir === 'left' && col > 0) return { row, col: col - 1 };
        if (dir === 'right' && col < predictions.length - 1) return { row, col: col + 1 };
        return prev;
      }

      const maxRow = keyGrid.length - 1;

      if (dir === 'up') {
        if (row === 0 && predictions.some(p => p)) return { row: -1, col: 0 };
        if (row > 0) return { row: row - 1, col: getClosestColumn(col, keyGrid[row - 1]) };
      }
      if (dir === 'down' && row < maxRow) {
        return { row: row + 1, col: getClosestColumn(col, keyGrid[row + 1]) };
      }
      if (dir === 'left' && col > 0) return { row, col: col - 1 };
      if (dir === 'right' && col < keyGrid[row].length - 1) return { row, col: col + 1 };

      return prev;
    });
  };

  const handleSelect = () => {
    if (cursor.row === -1) {
      const word = predictions[cursor.col];
      if (word) {
        const words = input.trim().split(" ");
        words.pop();
        setInput(words.concat(word).join(" ") + " ");
      }
      return;
    }

    const char = keyGrid[cursor.row][cursor.col];
    if (char === 'Clr') setInput('');
    else if (char === 'Del') setInput((prev) => prev.slice(0, -1));
    else if (char === 'Space') setInput((prev) => prev + ' ');
    else setInput((prev) => prev + char.toLowerCase());
  };

  return (
    <div className="outer-container">
      <div className="speller-container">
        <div className="display">
          <strong>Input:</strong>
          <span className="text input-text">{input}<span className="cursor">|</span></span>
        </div>

        <button className="select-btn" onClick={handleSelect}>Select</button>

        <div className="arrows">
          <button onClick={() => handleMove('up')}>↑</button>
        </div>

        <div className="prediction-row">
          {predictions.map((word, idx) => (
            <button
              key={idx}
              className={cursor.row === -1 && cursor.col === idx ? 'selected-key blink' : ''}
            >
              {word || '\u00A0'}
            </button>
          ))}
        </div>

        <div className="horizontal">
          <button onClick={() => handleMove('left')}>←</button>

          <div className="grid">
            {keyGrid.map((row, rowIndex) => (
              <div key={rowIndex} className="row">
                {row.map((char, colIndex) => {
                  const isSelected = rowIndex === cursor.row && colIndex === cursor.col;
                  return (
                    <button
                      key={colIndex}
                      className={isSelected ? 'selected-key blink' : ''}
                    >
                      {char}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>

          <button onClick={() => handleMove('right')}>→</button>
        </div>

        <div className="arrows">
          <button onClick={() => handleMove('down')}>↓</button>
        </div>
      </div>
    </div>
  );
}
