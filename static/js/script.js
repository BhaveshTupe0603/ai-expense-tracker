let allExpenses = [];
let expenseChart = null;

document.addEventListener("DOMContentLoaded", () => {
    const d = document.getElementById('date');
    if(d) d.valueAsDate = new Date();
    
    if(document.getElementById('expense-table')) {
        loadExpenses();
        loadBudgets(); 
    }
    
    const chatInput = document.getElementById('chat-input');
    if(chatInput) chatInput.addEventListener('keypress', (e) => { if(e.key==='Enter') sendMessage(); });

    const searchInput = document.getElementById('search-input');
    if(searchInput) searchInput.addEventListener('keypress', (e) => { 
        if(e.key==='Enter') loadExpenses(); 
    });
});

// --- FILTER LOGIC ---

// 1. Helper: Toggle Select All Checkboxes
function toggleSelectAll(source) {
    const checkboxes = document.querySelectorAll('.month-check');
    checkboxes.forEach(cb => cb.checked = source.checked);
}

// 2. Load Expenses & Update UI Text
async function loadExpenses() {
    const search = document.getElementById('search-input')?.value || '';
    
    // Get Checked Months
    const checkboxes = document.querySelectorAll('.month-check:checked');
    const selectedMonths = Array.from(checkboxes).map(cb => cb.value);
    
    // Update Button Text Logic
    const btnText = document.getElementById('month-btn-text');
    if (btnText) {
        if (selectedMonths.length === 0 || selectedMonths.length === 12) {
            btnText.innerText = "🗓️ All Months";
        } else if (selectedMonths.length <= 3) {
            // Show names like "Jan, Feb"
            const monthNames = { 
                "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", 
                "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", 
                "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec" 
            };
            // Sort keys just in case
            const sorted = selectedMonths.sort();
            const names = sorted.map(m => monthNames[m]).join(", ");
            btnText.innerText = `🗓️ ${names}`;
        } else {
            // Show count if too many
            btnText.innerText = `🗓️ ${selectedMonths.length} Selected`;
        }
    }

    // Build Query URL
    let url = `/api/expenses?t=${new Date().getTime()}`; 
    if(selectedMonths.length > 0) {
        url += `&months=${selectedMonths.join(',')}`;
    }
    if(search) url += `&search=${encodeURIComponent(search)}`;

    const res = await fetch(url);
    allExpenses = await res.json();
    updateDashboard();
}

function updateDashboard() {
    let income = 0, expense = 0;
    const tbody = document.querySelector('#expense-table tbody');
    tbody.innerHTML = '';

    if (allExpenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="p-6 text-center text-slate-400">No transactions found matching your filters.</td></tr>';
    }

    allExpenses.forEach(ex => {
        if(ex.type === 'Credit') income += ex.amount; else expense += ex.amount;
        
        const row = `
        <tr class="hover:bg-slate-50 transition group border-b border-slate-50 last:border-none">
            <td class="p-4 pl-6 text-slate-500">${ex.date}</td>
            <td class="p-4">
                <div class="font-bold text-slate-700">${ex.merchant}</div>
                <div class="text-xs text-slate-400 mt-0.5 flex gap-2">
                    <span class="bg-slate-100 px-2 py-0.5 rounded text-slate-500">${ex.category}</span>
                    <span class="text-indigo-400">${ex.payment_mode}</span>
                </div>
            </td>
            <td class="p-4 font-bold ${ex.type==='Credit'?'text-emerald-500':'text-rose-500'}">
                ${ex.type==='Credit'?'+':'-'} ₹${ex.amount}
            </td>
            <td class="p-4 pr-6 text-right opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <button onclick="openEditModal(${ex.id})" class="text-amber-500 hover:bg-amber-50 p-2 rounded-lg transition mr-1">✎</button>
                <button onclick="deleteExpense(${ex.id})" class="text-rose-500 hover:bg-rose-50 p-2 rounded-lg transition">🗑</button>
            </td>
        </tr>`;
        tbody.innerHTML += row;
    });

    document.getElementById('kpi-income').innerText = `₹${income.toFixed(2)}`;
    document.getElementById('kpi-expense').innerText = `₹${expense.toFixed(2)}`;
    document.getElementById('kpi-balance').innerText = `₹${(income - expense).toFixed(2)}`;
    
    renderChart(allExpenses);
}

// Smart Chart Rendering (Daily vs Monthly View)
function renderChart(data) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    
    const checkedCount = document.querySelectorAll('.month-check:checked').length;
    const dates = data.map(d => new Date(d.date));
    
    let isMonthlyView = false;
    if (dates.length > 0) {
        const diffTime = Math.max(...dates) - Math.min(...dates);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        isMonthlyView = diffDays > 32 || checkedCount > 1 || checkedCount === 0;
    }

    const grouped = {};
    
    data.forEach(item => {
        if(item.type === 'Debit') {
            let key;
            if (isMonthlyView) {
                const dateObj = new Date(item.date);
                key = dateObj.toLocaleString('default', { month: 'short' }); 
            } else {
                key = item.date;
            }
            if(!grouped[key]) grouped[key] = 0;
            grouped[key] += item.amount;
        }
    });

    let labels;
    if (isMonthlyView) {
        const monthOrder = { "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12 };
        labels = Object.keys(grouped).sort((a, b) => monthOrder[a] - monthOrder[b]);
    } else {
        labels = Object.keys(grouped).sort();
    }
    
    if(expenseChart) expenseChart.destroy();
    
    let gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    expenseChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: [{ 
            label: isMonthlyView ? 'Monthly Spending' : 'Daily Spending', 
            data: labels.map(l => grouped[l]), 
            borderColor: '#6366f1', borderWidth: 3, backgroundColor: gradient, fill: true, tension: 0.4,
            pointBackgroundColor: '#fff', pointBorderColor: '#6366f1', pointRadius: 4
        }] },
        options: { 
            responsive: true, plugins: { legend: {display:false} },
            scales: { y: { grid: { borderDash: [4, 4], color: '#f1f5f9' }, beginAtZero: true }, x: { grid: { display: false } } }
        }
    });
}

// --- ACTIONS (Transaction) ---
async function submitExpense(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    data.amount = parseFloat(data.amount);
    data.source = 'manual';
    
    await fetch('/api/expenses', { 
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) 
    });
    
    e.target.reset(); 
    document.getElementById('date').valueAsDate = new Date(); 
    loadExpenses(); loadBudgets();
}

async function uploadImage() {
    const file = document.getElementById('file-input').files[0];
    if(!file) return;
    const formData = new FormData(); formData.append('file', file);
    document.getElementById('scan-status').innerText = "🤖 AI Analyzing...";
    
    const res = await fetch('/api/upload', { method:'POST', body:formData });
    const data = await res.json();
    document.getElementById('scan-status').innerText = "";

    document.getElementById('v-preview').src = data.image_url;
    document.getElementById('v-merchant').value = data.merchant;
    document.getElementById('v-date').value = data.date;
    document.getElementById('v-amount').value = data.amount;
    document.getElementById('v-category').value = data.category;
    document.getElementById('v-hash').value = data.image_hash;
    document.getElementById('v-flagged').value = data.is_flagged;
    
    openModal('verify-modal');
}

async function saveVerified() {
    const data = {
        merchant: document.getElementById('v-merchant').value,
        date: document.getElementById('v-date').value,
        amount: parseFloat(document.getElementById('v-amount').value),
        category: document.getElementById('v-category').value,
        type: 'Debit', source: 'scanned', payment_mode: 'Cash',
        image_hash: document.getElementById('v-hash').value,
        is_flagged: document.getElementById('v-flagged').value
    };
    await fetch('/api/expenses', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    closeModal('verify-modal'); loadExpenses(); loadBudgets();
}

// --- BUDGET LOGIC ---
async function loadBudgets() {
    const res = await fetch('/api/budgets');
    const budgets = await res.json();
    const container = document.getElementById('budget-list');
    
    if (!container) return;
    container.innerHTML = '';
    
    if(budgets.length === 0) {
        container.innerHTML = '<p class="text-slate-400 text-sm text-center">No budgets set. Create one for a trip or a month!</p>';
        return;
    }

    budgets.forEach(b => {
        let color = 'bg-emerald-500';
        if(b.percentage > 75) color = 'bg-amber-500';
        if(b.percentage > 90) color = 'bg-rose-500';

        const dateRange = `${new Date(b.start_date).toLocaleDateString('en-GB', {day:'numeric', month:'short'})} - ${new Date(b.end_date).toLocaleDateString('en-GB', {day:'numeric', month:'short'})}`;

        const html = `
            <div class="group relative">
                <div class="flex justify-between text-sm mb-1">
                    <div class="flex flex-col">
                        <span class="font-bold text-slate-700">${b.category}</span>
                        <span class="text-[10px] text-slate-400 font-medium">${dateRange}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-slate-500 text-xs">₹${b.spent} / ₹${b.limit}</span>
                        <button onclick='editBudget(${JSON.stringify(b)})' class="text-xs text-indigo-500 hover:bg-indigo-50 p-1 rounded">✎</button>
                        <button onclick='deleteBudget(${b.id})' class="text-xs text-rose-500 hover:bg-rose-50 p-1 rounded">✕</button>
                    </div>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                    <div class="${color} h-2.5 rounded-full transition-all duration-1000" style="width: ${b.percentage}%"></div>
                </div>
            </div>`;
        container.innerHTML += html;
    });
}

function openBudgetModal() {
    document.getElementById('budget-id').value = '';
    document.getElementById('budget-modal-title').innerText = "New Budget 🎯";
    document.getElementById('budget-amount').value = '';
    
    const today = new Date();
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    document.getElementById('budget-start').valueAsDate = today;
    document.getElementById('budget-end').valueAsDate = lastDay;
    
    openModal('budget-modal');
}

function editBudget(b) {
    document.getElementById('budget-id').value = b.id;
    document.getElementById('budget-modal-title').innerText = "Edit Budget ✏️";
    document.getElementById('budget-category').value = b.category;
    document.getElementById('budget-amount').value = b.limit;
    document.getElementById('budget-start').value = b.start_date;
    document.getElementById('budget-end').value = b.end_date;
    openModal('budget-modal');
}

async function saveBudget() {
    const id = document.getElementById('budget-id').value;
    const data = {
        category: document.getElementById('budget-category').value,
        amount: parseFloat(document.getElementById('budget-amount').value),
        start_date: document.getElementById('budget-start').value,
        end_date: document.getElementById('budget-end').value
    };

    if(!data.amount || !data.start_date || !data.end_date) return alert("Please fill all fields");

    let url = '/api/budgets';
    let method = 'POST';

    if(id) {
        url = `/api/budgets/${id}`;
        method = 'PUT';
    }

    await fetch(url, { method: method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    closeModal('budget-modal'); loadBudgets();
}

async function deleteBudget(id) {
    if(confirm("Delete this budget?")) {
        await fetch(`/api/budgets/${id}`, { method: 'DELETE' });
        loadBudgets();
    }
}

// --- OTHER UTILS ---
function openEditModal(id) {
    const exp = allExpenses.find(e => e.id === id);
    document.getElementById('edit-id').value = exp.id;
    document.getElementById('edit-date').value = exp.date;
    document.getElementById('edit-merchant').value = exp.merchant;
    document.getElementById('edit-amount').value = exp.amount;
    document.getElementById('edit-category').value = exp.category;
    document.getElementsByName('edit-type').forEach(r => r.checked = r.value === exp.type);
    openModal('edit-modal');
}

async function saveEdit() {
    const id = document.getElementById('edit-id').value;
    const data = {
        date: document.getElementById('edit-date').value,
        merchant: document.getElementById('edit-merchant').value,
        amount: parseFloat(document.getElementById('edit-amount').value),
        category: document.getElementById('edit-category').value,
        type: document.querySelector('input[name="edit-type"]:checked').value
    };
    await fetch(`/api/expenses/${id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
    closeModal('edit-modal'); loadExpenses(); loadBudgets();
}

async function deleteExpense(id) {
    if(confirm("Are you sure?")) { 
        await fetch(`/api/expenses/${id}`, { method:'DELETE' }); 
        loadExpenses(); loadBudgets();
    }
}

async function saveProfile() {
    const data = {
        name: document.getElementById('p-name').value,
        age: document.getElementById('p-age').value,
        occupation: document.getElementById('p-occupation').value,
        role: document.getElementById('p-role').value
    };
    
    const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    
    if(res.ok) {
        alert("Profile Updated Successfully!");
        location.reload(); 
    }
}

function openModal(id) {
    const el = document.getElementById(id);
    if(!el) return;
    el.classList.remove('hidden');
    setTimeout(() => {
        el.classList.remove('opacity-0');
        el.querySelector('div').classList.remove('scale-95');
        el.querySelector('div').classList.add('scale-100');
    }, 10);
}

function closeModal(id) {
    const el = document.getElementById(id);
    if(!el) return;
    el.classList.add('opacity-0');
    el.querySelector('div').classList.remove('scale-100');
    el.querySelector('div').classList.add('scale-95');
    setTimeout(() => el.classList.add('hidden'), 300);
}

function toggleChat() { document.getElementById('chat-window').classList.toggle('hidden'); }

async function sendMessage() {
    const input = document.getElementById('chat-input');
    if(!input.value) return;
    const msg = input.value; input.value='';
    const box = document.getElementById('chat-messages');
    
    box.innerHTML += `<div class="bg-indigo-600 text-white p-3 rounded-2xl rounded-br-none self-end max-w-xs text-sm shadow-md">${msg}</div>`;
    box.scrollTop = box.scrollHeight;

    const res = await fetch('/api/chat', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg}) });
    const data = await res.json();
    
    box.innerHTML += `<div class="bg-white border border-slate-200 text-slate-700 p-3 rounded-2xl rounded-bl-none self-start max-w-xs text-sm shadow-sm">${data.response}</div>`;
    box.scrollTop = box.scrollHeight;
}