let currentYear = 2025;
let selectedMonth = null;
let username = null;
let role = "guest";

// async function getUserInfo() {
//     try {
//       const response = await fetch("/me");
//       if (response.ok) {
//         const user = await response.json();
//         username = user.username;
//         //name = user.name || "User";
//         role = user.role || "guest";
//       }
//     } catch {}
// }

const months = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"];

document.addEventListener("DOMContentLoaded", function() {
    loadYearSummary();
});

async function loadYearSummary() {
    currentYear = document.getElementById('yearSelect').value;
    
    try {
        const response = await fetch(`/income_records/?username=${encodeURIComponent(userData.username)}&year=${currentYear}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySummary(data);
        } else {
            console.error('Failed to load summary data');
            alert('Failed to load summary data. Please try again.');
        }
    } catch (error) {
        console.error('Error loading summary:', error);
        alert('Error loading summary data. Please check your connection.');
    }
}

function displaySummary(data) {
    // Update summary cards
    document.getElementById('yearlyTotal').textContent = `₹${data.yearly_total.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('yearlyCount').textContent = `${data.yearly_count} records`;
    
    // Reset monthly total
    document.getElementById('monthlyTotal').textContent = '₹0';
    document.getElementById('monthlyCount').textContent = 'Click a month to view';
    
    // Create monthly grid
    const monthlyGrid = document.getElementById('monthlyGrid');
    monthlyGrid.innerHTML = '';
    
    months.forEach(month => {
        const monthData = data.monthly_summary[month];
        const monthCard = document.createElement('div');
        monthCard.className = 'month-card';
        monthCard.onclick = () => selectMonth(month, monthData.total, monthData.count);
        
        monthCard.innerHTML = `
            <div class="month-name">${month}</div>
            <div class="month-amount">₹${monthData.total.toLocaleString('en-IN')}</div>
            <small>${monthData.count} records</small>
        `;
        
        monthlyGrid.appendChild(monthCard);
    });
    
    // Hide records section when year changes
    document.getElementById('recordsSection').style.display = 'none';
    selectedMonth = null;
}

async function selectMonth(month, monthTotal, recordCount) {
    selectedMonth = month;
    
    // Update UI
    document.querySelectorAll('.month-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.target.closest('.month-card').classList.add('selected');
    
    // Update month total
    document.getElementById('monthlyTotal').textContent = `₹${monthTotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('monthlyCount').textContent = `${recordCount} records`;
    
    // Load detailed records
    try {
        const response = await fetch(`/income_records/?username=${encodeURIComponent(userData.username)}&year=${currentYear}&month=${month}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            displayMonthRecords(data.month_records, data.month_total);
        } else {
            console.error('Failed to load month records');
            //alert('Failed to load month records. Please try again.');
        }
    } catch (error) {
        console.error('Error loading month records:', error);
        //alert('Error loading month records. Please check your connection.');
    }
}

function displayMonthRecords(records, total) {
    const recordsSection = document.getElementById('recordsSection');
    const recordsTitle = document.getElementById('recordsTitle');
    const tableBody = document.getElementById('recordsTableBody');
    
    recordsTitle.textContent = `📋 Records for ${selectedMonth} ${currentYear}`;
    recordsSection.style.display = 'block';
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    if (records.length === 0) {
        const noDataRow = document.createElement('tr');
        noDataRow.innerHTML = `
            <td colspan="5" style="text-align: center; color: #6c757d; font-style: italic;">
                No records found for ${selectedMonth} ${currentYear}
            </td>
        `;
        tableBody.appendChild(noDataRow);
        return;
    }
    
    // Add record rows
    records.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(record.date).toLocaleDateString('en-IN')}</td>
            <td>${record.owner_name || 'N/A'}</td>
            <td>${record.paid_by}</td>
            <td>₹${record.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
            <td>User ID: ${record.created_by}</td>
        `;
        tableBody.appendChild(row);
    });
    
    // Add total row
    const totalRow = document.createElement('tr');
    totalRow.className = 'total-row';
    totalRow.innerHTML = `
        <td colspan="3"><strong>📊 TOTAL</strong></td>
        <td><strong>₹${total.toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></td>
        <td><strong>${records.length} records</strong></td>
    `;
    tableBody.appendChild(totalRow);
    
    // Scroll to records section
    recordsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}