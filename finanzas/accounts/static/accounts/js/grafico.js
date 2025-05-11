    const segments = [];
    let ranges = [];

    function getRandomColor() {
      let color = '#';
      for (let i = 0; i < 6; i++) {
        color += Math.floor(Math.random() * 16).toString(16);
      }
      return color.padEnd(7, '0');
    }

    function updateChart() {
      const donut = document.getElementById('donut-chart');
      const legend = document.getElementById('legend');
      
      const total = segments.reduce((sum, s) => sum + s.value, 0);
      let start = 0;
      ranges = [];

      const gradient = segments.map(seg => {
        const percent = (seg.value / total) * 100;
        const end = start + percent;
        ranges.push({ start, end, segment: seg });
        const str = `${seg.color} ${start}% ${end}%`;
        start = end;
        return str;
      }).join(', ');

      donut.style.background = `conic-gradient(${gradient || '#f7f9fb 0% 100%'})`;
      donut.setAttribute('data-total', total > 0 ? `${Math.round((segments.reduce((max, s) => s.value > max.value ? s : max, segments[0] || { value: 0 }).value / total) * 100)}%` : '$0');

      legend.innerHTML = segments.map(seg => {
        const percent = ((seg.value / total) * 100).toFixed(1);
        return `<div class="legend-item"><span class="color-box" style="background:${seg.color}"></span> ${seg.label}: ${percent}%</div>`;
      }).join('');
    }

    function addExpense() {
      const labelInput = document.getElementById('label');
      const valueInput = document.getElementById('value');
      const label = labelInput.value.trim();
      const value = parseFloat(valueInput.value);
      if (!label || isNaN(value) || value <= 0) {
        alert('Ingrese una categoría y un monto válido.');
        return;
      }

      const existing = segments.find(s => s.label.toLowerCase() === label.toLowerCase());
      if (existing) {
        existing.value += value;
      } else {
        const color = getRandomColor();
        segments.push({ label, value, color });
      }

      updateChart();
      labelInput.value = '';
      valueInput.value = '';
    }
