const form = document.getElementById('expense-form');
const list = document.getElementById('expense-list');
const totalDisplay = document.getElementById('total');
const chartCtx = document.getElementById('chart').getContext('2d');
let chart;

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const category = document.getElementById('category').value;
  const amount = parseFloat(document.getElementById('amount').value);

  await fetch('/api/expenses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category, amount })
  });

  form.reset();
  loadExpenses();
});

async function loadExpenses() {
  const res = await fetch('/api/expenses');
  const data = await res.json();

  let total = 0;
  const categoryMap = {};
  list.innerHTML = '';

  data.forEach(exp => {
    total += exp.amount;
    categoryMap[exp.category] = (categoryMap[exp.category] || 0) + exp.amount;

    const li = document.createElement('li');
    li.className = "bg-white bg-opacity-10 p-2 rounded flex justify-between";
    li.innerHTML = `<span>${exp.category}</span><span class="text-green-300 font-bold">₹${exp.amount}</span>`;
    list.appendChild(li);
  });

  totalDisplay.textContent = `Total: ₹${total}`;

  if (chart) chart.destroy();
  chart = new Chart(chartCtx, {
    type: 'pie',
    data: {
      labels: Object.keys(categoryMap),
      datasets: [{
        data: Object.values(categoryMap),
        backgroundColor: ['#60a5fa', '#f87171', '#34d399', '#fbbf24', '#a78bfa']
      }]
    },
    options: {
      plugins: {
        legend: { labels: { color: 'white' } }
      }
    }
  });
}

loadExpenses();
