var display = document.getElementById('result');
var expr    = document.getElementById('expression');
var val = '0', first = null, op = null, fresh = false;

function clean(n) { return parseFloat(n.toPrecision(12)).toString(); }

function render() {
    display.textContent = val;
    var l = val.replace('-','').length;
    display.classList.toggle('small',  l > 9);
    display.classList.toggle('xsmall', l > 12);
}

function digit(d) {
    if (fresh) { val = d; fresh = false; }
    else { val = val === '0' ? d : val + d; }
}

function dot() {
    if (fresh) { val = '0.'; fresh = false; return; }
    if (val.indexOf('.') < 0) val += '.';
}

function calc(a, b, o) {
    if (o === '+') return a + b;
    if (o === '-') return a - b;
    if (o === 'x') return a * b;
    if (o === '/') return b === 0 ? null : a / b;
    return b;
}

function setOp(next) {
    var cur = parseFloat(val);
    if (op && !fresh) {
        var r = calc(first, cur, op);
        if (r === null) { val = 'Error'; expr.textContent = ''; op = null; first = null; render(); return; }
        val = clean(r); first = r;
    } else { first = cur; }
    expr.textContent = clean(first) + ' ' + next;
    op = next; fresh = true;
    document.querySelectorAll('.btn-op').forEach(function(b){ b.classList.toggle('active', b.dataset.value === next); });
    render();
}

function equals() {
    if (!op || fresh) return;
    var cur = parseFloat(val);
    var r = calc(first, cur, op);
    expr.textContent = clean(first) + ' ' + op + ' ' + clean(cur) + ' =';
    val = r === null ? 'Error' : clean(r);
    op = null; first = null; fresh = false;
    document.querySelectorAll('.btn-op').forEach(function(b){ b.classList.remove('active'); });
    render();
}

function clear() {
    val = '0'; first = null; op = null; fresh = false; expr.textContent = '';
    document.querySelectorAll('.btn-op').forEach(function(b){ b.classList.remove('active'); });
    render();
}

function sign() {
    if (val === '0' || val === 'Error') return;
    val = val.charAt(0) === '-' ? val.slice(1) : '-' + val;
    render();
}

function pct() {
    var n = parseFloat(val);
    if (!isNaN(n)) { val = clean(n / 100); render(); }
}

function back() {
    if (val === 'Error') { clear(); return; }
    val = val.length > 1 ? val.slice(0, -1) : '0';
    render();
}

function syncAC() {
    var b = document.querySelector('[data-action="clear"]');
    if (b) b.textContent = (val !== '0' || op) ? 'C' : 'AC';
}

document.querySelector('.buttons').addEventListener('click', function(e) {
    var b = e.target.closest('.btn');
    if (!b) return;
    var a = b.dataset.action, v = b.dataset.value;
    if      (a === 'digit')   digit(v);
    else if (a === 'decimal') dot();
    else if (a === 'op')      setOp(v);
    else if (a === 'equals')  equals();
    else if (a === 'clear')   clear();
    else if (a === 'sign')    sign();
    else if (a === 'percent') pct();
    syncAC(); render();
});

document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var k = e.key;
    if      (k >= '0' && k <= '9')      digit(k);
    else if (k === '.' || k === ',')     dot();
    else if (k === '+')                  setOp('+');
    else if (k === '-')                  setOp('-');
    else if (k === '*')                  setOp('x');
    else if (k === '/')                  { e.preventDefault(); setOp('/'); }
    else if (k === 'Enter' || k === '=') equals();
    else if (k === 'Backspace')          back();
    else if (k === 'Escape')             clear();
    else if (k === '%')                  pct();
    else return;
    syncAC(); render();
});

render();
