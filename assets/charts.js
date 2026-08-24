(() => {
  const svg = document.querySelector('[data-budget-trend]');
  if (!svg) return;

  const points = [
    { year: 2021, value: 3731.2, type: 'fact' },
    { year: 2022, value: 4051.5, type: 'fact' },
    { year: 2023, value: 5243.0, type: 'fact' },
    { year: 2024, value: 5101.1, type: 'fact' },
    { year: 2025, value: 5924.1, type: 'fact' },
    { year: 2026, value: 6440.3, type: 'plan' },
    { year: 2027, value: 6834.0, type: 'plan' },
    { year: 2028, value: 9134.2, type: 'plan' }
  ];
  const W = 760, H = 350, left = 58, right = 24, top = 28, bottom = 54;
  const min = 3000, max = 9500;
  const x = (i) => left + i * ((W - left - right) / (points.length - 1));
  const y = (v) => top + (max - v) * ((H - top - bottom) / (max - min));
  const ns = 'http://www.w3.org/2000/svg';
  const add = (tag, attrs = {}, text = '') => {
    const node = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([key, val]) => node.setAttribute(key, val));
    if (text) node.textContent = text;
    svg.append(node);
    return node;
  };

  [4000, 6000, 8000].forEach((tick) => {
    add('line', { x1: left, x2: W-right, y1: y(tick), y2: y(tick), stroke: '#d6d0c5', 'stroke-width': 1 });
    add('text', { x: left-10, y: y(tick)+4, 'text-anchor':'end', fill:'#6a7472', 'font-size':12 }, `${tick/1000} млрд`);
  });

  points.forEach((point, i) => add('text', { x:x(i), y:H-24, 'text-anchor':'middle', fill:'#53605e', 'font-size':12 }, point.year));
  const actual = points.slice(0,5).map((p,i)=>`${x(i)},${y(p.value)}`).join(' ');
  const planned = points.slice(4).map((p,i)=>`${x(i+4)},${y(p.value)}`).join(' ');
  add('polyline', { points:actual, fill:'none', stroke:'#176e66', 'stroke-width':4, 'stroke-linecap':'round', 'stroke-linejoin':'round' });
  add('polyline', { points:planned, fill:'none', stroke:'#b6542c', 'stroke-width':4, 'stroke-dasharray':'9 7', 'stroke-linecap':'round', 'stroke-linejoin':'round' });

  points.forEach((point, i) => {
    const color = point.type === 'fact' ? '#176e66' : '#b6542c';
    add('circle', { cx:x(i), cy:y(point.value), r:5.5, fill:'#fffdf8', stroke:color, 'stroke-width':3 });
    add('text', { x:x(i), y:y(point.value)-13, 'text-anchor':'middle', fill:'#172423', 'font-size':11, 'font-weight':700 }, `${(point.value/1000).toFixed(point.value % 1000 ? 1 : 0).replace('.', ',')}`);
  });

  add('line', { x1:520, x2:548, y1:18, y2:18, stroke:'#176e66', 'stroke-width':4 });
  add('text', { x:555, y:22, fill:'#53605e', 'font-size':11 }, 'факт');
  add('line', { x1:620, x2:648, y1:18, y2:18, stroke:'#b6542c', 'stroke-width':4, 'stroke-dasharray':'7 5' });
  add('text', { x:655, y:22, fill:'#53605e', 'font-size':11 }, 'план');
})();

