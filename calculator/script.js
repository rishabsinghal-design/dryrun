/**
 * Calculator – script.js
 *
 * Supports: +, −, ×, ÷, %, +/− toggle, decimal point,
 *           chained operations, keyboard input, and
 *           error handling (division by zero).
 */

'use strict';

// ─── State ────────────────────────────────────────────────────────────────────

const state = {
  currentValue:  '0',   // number currently being built
  previousValue: '',    // left-hand operand
  operator:      null,  // pending operator symbol
  shouldReset:   false, // flag: next digit press starts a fresh number
  expression:    '',    // text shown in the small expression line
};

// ─── DOM refs ─────────────────────────────────────────────────────────────────

const resultEl     = document.getElementById('result');
const expressionEl = document.getElementById('expression');

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Map display symbols to JS operators.
 */
const OP_MAP = { '÷': '/', '×': '*', '−': '-', '+': '+' };

/**
 * Safely evaluate two operands with the given operator.
 * Returns a string result (or 'Error').
 */
function calculate(a, op, b) {
  const numA = parseFloat(a);
  const numB = parseFloat(b);

  if (isNaN(numA) || isNaN(numB)) return 'Error';

  let result;
  switch (op) {
    case '÷':
      if (numB === 0) return 'Error';
      result = numA / numB;
      break;
    case '×': result = numA * numB; break;
    case '−': result = numA - numB; break;
    case '+': result = numA + numB; break;
    default:  return 'Error';
  }

  // Avoid floating-point noise (e.g. 0.1 + 0.2 = 0.30000000000000004)
  result = parseFloat(result.toPrecision(12));

  return String(result);
}

/**
 * Format a numeric string for display (add commas, cap length).
 */
function formatDisplay(value) {
  if (value === 'Error') return 'Error';

  const num = parseFloat(value);
  if (isNaN(num)) return value;

  // Use toLocaleString only for the integer part; keep decimals raw
  const [intPart, decPart] = value.split('.');
  const formattedInt = parseInt(intPart, 10).toLocaleString('en-US');

  return decPart !== undefined ? `${formattedInt}.${decPart}` : formattedInt;
}

/**
 * Update the display elements and adjust font size.
 */
function updateDisplay() {
  const formatted = formatDisplay(state.currentValue);
  resultEl.textContent = formatted;
  expressionEl.textContent = state.expression;

  // Responsive font size
  resultEl.classList.remove('small', 'xsmall');
  if (formatted.length > 12) resultEl.classList.add('xsmall');
  else if (formatted.length > 8) resultEl.classList.add('small');
}

/**
 * Highlight / un-highlight the active operator button.
 */
function setActiveOperator(op) {
  document.querySelectorAll('.btn--operator').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.value === op);
  });
}

// ─── Action Handlers ──────────────────────────────────────────────────────────

function handleDigit(digit) {
  if (state.shouldReset) {
    state.currentValue = digit;
    state.shouldReset  = false;
  } else {
    // Prevent multiple leading zeros
    if (state.currentValue === '0' && digit !== '.') {
      state.currentValue = digit;
    } else {
      // Cap input length
      if (state.currentValue.replace(/[^0-9]/g, '').length >= 12) return;
      state.currentValue += digit;
    }
  }
  updateDisplay();
}

function handleDecimal() {
  if (state.shouldReset) {
    state.currentValue = '0.';
    state.shouldReset  = false;
    updateDisplay();
    return;
  }
  if (!state.currentValue.includes('.')) {
    state.currentValue += '.';
    updateDisplay();
  }
}

function handleOperator(op) {
  // If there's a pending operation, resolve it first (chaining)
  if (state.operator && !state.shouldReset) {
    const result = calculate(state.previousValue, state.operator, state.currentValue);
    state.currentValue  = result;
    state.previousValue = result;
  } else {
    state.previousValue = state.currentValue;
  }

  state.operator    = op;
  state.shouldReset = true;
  state.expression  = `${formatDisplay(state.previousValue)} ${op}`;

  setActiveOperator(op);
  updateDisplay();
}

function handleEquals() {
  if (!state.operator || !state.previousValue) return;

  const expression = `${formatDisplay(state.previousValue)} ${state.operator} ${formatDisplay(state.currentValue)} =`;
  const result     = calculate(state.previousValue, state.operator, state.currentValue);

  state.expression    = expression;
  state.currentValue  = result;
  state.previousValue = '';
  state.operator      = null;
  state.shouldReset   = true;

  setActiveOperator(null);
  updateDisplay();
}

function handleClear() {
  state.currentValue  = '0';
  state.previousValue = '';
  state.operator      = null;
  state.shouldReset   = false;
  state.expression    = '';

  setActiveOperator(null);
  updateDisplay();
}

function handleSign() {
  if (state.currentValue === '0' || state.currentValue === 'Error') return;
  state.currentValue = state.currentValue.startsWith('-')
    ? state.currentValue.slice(1)
    : '-' + state.currentValue;
  updateDisplay();
}

function handlePercent() {
  if (state.currentValue === 'Error') return;
  state.currentValue = String(parseFloat(state.currentValue) / 100);
  updateDisplay();
}

// ─── Event Delegation (click) ─────────────────────────────────────────────────

document.querySelector('.buttons').addEventListener('click', (e) => {
  const btn = e.target.closest('.btn');
  if (!btn) return;

  const { action, value } = btn.dataset;

  switch (action) {
    case 'digit':    handleDigit(value);    break;
    case 'decimal':  handleDecimal();       break;
    case 'operator': handleOperator(value); break;
    case 'equals':   handleEquals();        break;
    case 'clear':    handleClear();         break;
    case 'sign':     handleSign();          break;
    case 'percent':  handlePercent();       break;
  }
});

// ─── Keyboard Support ─────────────────────────────────────────────────────────

const KEY_MAP = {
  '0': () => handleDigit('0'),
  '1': () => handleDigit('1'),
  '2': () => handleDigit('2'),
  '3': () => handleDigit('3'),
  '4': () => handleDigit('4'),
  '5': () => handleDigit('5'),
  '6': () => handleDigit('6'),
  '7': () => handleDigit('7'),
  '8': () => handleDigit('8'),
  '9': () => handleDigit('9'),
  '.': () => handleDecimal(),
  ',': () => handleDecimal(),
  '+': () => handleOperator('+'),
  '-': () => handleOperator('−'),
  '*': () => handleOperator('×'),
  '/': () => handleOperator('÷'),
  'Enter':     () => handleEquals(),
  '=':         () => handleEquals(),
  'Backspace': () => {
    if (state.shouldReset || state.currentValue === 'Error') return;
    state.currentValue =
      state.currentValue.length > 1
        ? state.currentValue.slice(0, -1)
        : '0';
    updateDisplay();
  },
  'Escape': () => handleClear(),
  '%':      () => handlePercent(),
};

document.addEventListener('keydown', (e) => {
  if (KEY_MAP[e.key]) {
    e.preventDefault();
    KEY_MAP[e.key]();
  }
});

// ─── Init ─────────────────────────────────────────────────────────────────────

updateDisplay();
