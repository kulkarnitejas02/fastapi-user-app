let currentYear = 2025;
let selectedMonth = null;

const months = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"];   

document.addEventListener("DOMContentLoaded", function() {
    loadYearSummaryExpense();
});

async function loadYearSummaryExpense() {

    currentYear = document.getElementById('yearSelect').value;

    try{
        const response = await fetch(`/expense_records/?username=${encodeURIComponent(userData.username)}&year=${currentYear}`,{
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok){
            const data = await response.json();
            displaySummaryExpense(data);
        } else {
            console.error('Failed to load summary data');
            alert('Failed to load summary data. Please try again.');
        }
    }catch (error){
        console.error('Error loading summary:', error);
        alert('Error loading summary data. Please check your connection.');
    }

}

function displaySummaryExpense(data) {
    // Update summary cards
    document.getElementById('yearlyTotalExpense').textContent = `₹${data.yearly_total.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('yearlyCountExpense').textContent = `${data.yearly_count} records`;

    // Reset monthly total
    document.getElementById('monthlyTotalExpense').textContent = '₹0';
    document.getElementById('monthlyCountExpense').textContent = 'Click a month to view';   

    // Create monthly grid
    const monthlyGrid = document.getElementById('monthlyGridExpense');
    monthlyGrid.innerHTML = '';

    months.forEach(month => {
        const monthData = data.monthly_summary[month];
        const monthCard = document.createElement('div');
        monthCard.className = 'month-card';
        monthCard.onclick = () => selectMonthExpense(month, monthData.total, monthData.count);

        monthCard.innerHTML = `
            <h3>${month}</h3>
            <p>Total: ₹${monthData.total.toLocaleString('en-IN', {minimumFractionDigits: 2})}</p>
            <p>Count: ${monthData.count} records</p>
        `;
        monthlyGrid.appendChild(monthCard);
    });
}

async function selectMonthExpense(month, monthTotal, count) {
    selectedMonth = month;

    //update UI
    document.querySelectorAll('.month-card').forEach(card => {
        card.classList.remove('selected-month');
    });
    event.target.closest('.month-card').classList.add('selected-month');

    //Update month total
    document.getElementById('monthlyTotalExpense').textContent = `₹${monthTotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('monthlyCountExpense').textContent = `${count} records`;
    // Load detailed expense records for the selected month
    try{
        const response = await fetch(`/expense_records/?username=${encodeURIComponent(userData.username)}&year=${currentYear}&month=${month}`,{
            method: 'GET',
            credentials: 'include'
        });
        if (response.ok){
            const data = await response.json();
            displayExpenseMonthRecords(data.month_records, data.month_total);
        } else {
            console.error('Failed to load monthly records');
            alert('Failed to load monthly records. Please try again.');
        }
    }catch (error){
        console.error('Error loading monthly records:', error);
        alert('Error loading monthly records. Please check your connection.');
    }
}

function displayExpenseMonthRecords(records, monthTotal) {
    const recordsSection = document.getElementById('expenseRecordsSection');
    const recordsTitle = document.getElementById('expenseRecordsTitle');
    const tableBody = document.getElementById('expenseRecordsTableBody');

    // Update title
    recordsTitle.textContent = `Records for ${selectedMonth} ${currentYear}`;
    recordsSection.style.display = 'block';
    // Clear previous records
    tableBody.innerHTML = '';

    // Populate table with new records
    records.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.date}</td>
            <td>${record.expense_name}</td>
            <td>${record.description}</td>
            <td>₹${record.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
            <td>${record.created_by}</td>
        `;
        tableBody.appendChild(row);
    });

    // Show records section

    const totalRow = document.createElement('tr');
    totalRow.innerHTML = `
        <td colspan="3"><strong>Total</strong></td>
        <td>₹${monthTotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td></td>
    `;
    tableBody.appendChild(totalRow);
    recordsSection.style.display = 'block';

    recordsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}