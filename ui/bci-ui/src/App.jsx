// App.jsx
import { useState, useEffect } from 'react';
import './App.css';

const keyGrid = [
  ['Space', 'L', 'Del'],
  ['F', 'T', 'J'],
  ['Q', 'V', 'M', 'I', 'O', 'K', '.'],
  [',', 'U', 'A', 'N', 'E', 'S', 'D', 'C'],
  ['G', 'P', 'W', 'R', 'B', 'Y', '-'],
  ['X', 'H', 'Z', 'Clr']
];

const keyNavMap = {
  // Top row to suggestion row
  '0_0': { up: '-1_0' }, // Space ↑ → Left suggestion
  '0_1': { up: '-1_1' }, // L ↑ → Middle suggestion
  '0_2': { up: '-1_2' }, // Del ↑ → Right suggestion

  // Suggestion row to top row (we fake keys for this using the same structure)
  '-1_0': { down: '0_0' }, // Left suggestion ↓ → Space
  '-1_1': { down: '0_1' }, // Middle suggestion ↓ → L
  '-1_2': { down: '0_2' }, // Right suggestion ↓ → Del

  // Row 1
  '1_0': { down: '2_2' }, // F → M
  '1_2': { down: '2_4' }, // J → O

  // Row 2
  '2_5': { down: '3_6' }, // K → D

  // Row 3
  '3_4': { up: '2_4', down: '4_3' }, // E → O, E ↓ R
  '3_3': { up: '2_3', down: '4_2' }, // N → I, N ↓ W
  '3_5': { up: '2_5', down: '4_4' }, // S → K, S ↓ B
  '3_6': { down: '4_5' },            // D → Y
  '3_7': { down: '4_6' },            // C → -

  // Row 4
  '4_3': { up: '3_4', down: '5_2' }, // R → E, R ↓ Z
  '4_4': { up: '3_5', down: '5_3' }, // B → S, B ↓ Clr
  '4_5': { up: '3_6' },              // Y ← D
  '4_6': { up: '3_7' },              // - ← C
  '4_1': { up: '5_0' },              // P ← X

  // Row 5
  '5_0': { up: '4_1' },              // X → P
  '5_2': { up: '4_3' },              // Z ← R
  '5_3': { up: '4_4' }               // Clr ← B
};


const getClosestColumn = (fromRow, fromCol, toRow) => {
  const fromRowLength = keyGrid[fromRow].length;
  const toRowLength = keyGrid[toRow].length;

  // X position of current key, normalized from 0 to 1
  const targetRatio = fromCol / (fromRowLength - 1);

  // Find the closest match in the next row
  let closest = 0;
  let minDiff = Infinity;

  for (let i = 0; i < keyGrid[toRow].length; i++) {
    const candidateRatio = i / (toRowLength - 1);
    const diff = Math.abs(candidateRatio - targetRatio);
    if (diff < minDiff) {
      minDiff = diff;
      closest = i;
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

      // Check if input ends with space (complete word) or is a partial word
      const endsWithSpace = input.endsWith(' ');
      const words = trimmed.split(" ");
      const lastWord = words[words.length - 1];
      
      // Use next-word prediction if:
      // 1. Input ends with space (just completed a word), OR
      // 2. Last word is complete (all letters) AND input doesn't end with space but we're at word boundary
      const shouldPredictNext = endsWithSpace || (lastWord && /^[a-zA-Z]+$/.test(lastWord) && input.endsWith(lastWord + ' '));
      
      // Use word completion if we're in the middle of typing a word
      const isPartialWord = !endsWithSpace && lastWord && /^[a-zA-Z]+$/.test(lastWord);

      let endpoint;
      if (shouldPredictNext) {
        endpoint = "predict_next";
      } else if (isPartialWord) {
        endpoint = "predict_complete";
      } else {
        // No predictions for empty input or non-alphabetic characters
        setPredictions(["", "", ""]);
        return;
      }

      try {
        const res = await fetch(`http://localhost:8000/${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ input: trimmed }),
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
      const maxRow = keyGrid.length - 1;
      const key = `${row}_${col}`;
      const navOverride = keyNavMap[key];
  
      // Handle UP
      if (dir === 'up') {
        if (navOverride?.up) {
          const [newRow, newCol] = navOverride.up.split('_').map(Number);
          return { row: newRow, col: newCol };
        }
  
        if (row === 0 && predictions.some(p => p)) {
          return { row: -1, col: 0 };
        }
  
        if (row > 0) {
          return {
            row: row - 1,
            col: getClosestColumn(row, col, row - 1)
          };
        }
      }
  
      // Handle DOWN
      if (dir === 'down') {
        if (navOverride?.down) {
          const [newRow, newCol] = navOverride.down.split('_').map(Number);
          return { row: newRow, col: newCol };
        }
  
        if (row === -1) {
          return { row: 0, col: 1 }; // default to center of top row if no override
        }
  
        if (row < maxRow) {
          return {
            row: row + 1,
            col: getClosestColumn(row, col, row + 1)
          };
        }
      }
  
      // Handle LEFT
      if (dir === 'left') {
        if (col > 0) {
          return { row, col: col - 1 };
        }
      }
  
      // Handle RIGHT
      if (dir === 'right') {
        const maxCol = row === -1 ? predictions.length - 1 : keyGrid[row].length - 1;
        if (col < maxCol) {
          return { row, col: col + 1 };
        }
      }
  
      // Default fallback (no movement)
      return prev;
    });
  };
  
  

  const handleSelect = () => {
    if (cursor.row === -1) {
      const word = predictions[cursor.col];
      if (word) {
        // Handle both word completion and next-word prediction
        const trimmed = input.trim();
        const endsWithSpace = input.endsWith(' ');
        
        if (endsWithSpace) {
          // Next-word prediction: just append the word
          setInput(input + word + ' ');
        } else {
          // Word completion: replace the partial word
          const words = trimmed.split(" ");
          words.pop(); // Remove partial word
          setInput(words.concat(word).join(" ") + " ");
        }
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
        <div className="input-block">
          <div className="display">
            <strong>Input:</strong>
            <span className="text input-text">{input}<span className="cursor">|</span></span>
          </div>

          <button className="select-btn" onClick={handleSelect}>Select</button>
        </div>

        <div className="arrows">
          <button className="arrow-btn up" onClick={() => handleMove('up')}>↑</button>
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
          <button className="arrow-btn left" onClick={() => handleMove('left')}>←</button>

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

          <button className="arrow-btn right" onClick={() => handleMove('right')}>→</button>
        </div>

        <div className="arrows">
          <button className="arrow-btn down" onClick={() => handleMove('down')}>↓</button>
        </div>
      </div>
    </div>
  );
}