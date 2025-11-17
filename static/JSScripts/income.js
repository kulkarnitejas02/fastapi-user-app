document.addEventListener("DOMContentLoaded", function() {
  let name = "User";
  let role = "guest";
  let username = "";
  let userid = 0;
  console.log("income.js loaded"); 
  async function getUserInfo() {
    try {
      const response = await fetch("/me");
      if (response.ok) {
        const user = await response.json();
        name = user.name || "User";
        role = user.role || "guest";
        username = user.username || "";
        userid = user.userid || 0;
        flat_number = user.flat_number || 0;
      }
      //console.log(username);
      //console.log(flat_number);
    } catch {}
    document.getElementById("welcome").innerText = `Welcome, ${name}!`;
    document.getElementById("role").innerText = `Role: ${role}`;
  }
  getUserInfo();

  // Income page logic
  const dashboardCard = document.getElementById("dashboard-card");
  const maintenanceFormCard = document.getElementById("Maintenance-form-card");
  const maintenanceTableCard = document.getElementById("Maintenance-table-card");
  if (dashboardCard) dashboardCard.classList.remove("hidden");
  if (maintenanceFormCard) maintenanceFormCard.classList.add("hidden");
  if (maintenanceTableCard) maintenanceTableCard.classList.add("hidden");

  const viewMaintenanceBtn = document.getElementById("view-Maintenance-btn");
  const addMaintenanceBtn = document.getElementById("add-Maintenance-btn");
  const backFromFormBtn = document.getElementById("back-from-form-btn");
  const backFromTableBtn = document.getElementById("back-from-table-btn");

  if (viewMaintenanceBtn) {
    viewMaintenanceBtn.onclick = function() {
      console.log("View Maintenance clicked");
      if (role === "secretary" || role === "treasurer" || role === "member") {
        if (dashboardCard) dashboardCard.classList.add("hidden");
        if (maintenanceFormCard) maintenanceFormCard.classList.add("hidden");
        if (maintenanceTableCard) maintenanceTableCard.classList.remove("hidden");
        // Don't load maintenance records automatically - wait for user to apply filters
        showFilterMessage();
      } else {
        alert("You do not have permission to view maintenance records.");
      }
    };
  }
  if (addMaintenanceBtn) {
    addMaintenanceBtn.onclick = function() {
      if (dashboardCard) dashboardCard.classList.add("hidden");
      if (maintenanceFormCard) maintenanceFormCard.classList.remove("hidden");
      if (maintenanceTableCard) maintenanceTableCard.classList.add("hidden");
    };
  }
  if (backFromFormBtn) {
    backFromFormBtn.onclick = function() {
      if (dashboardCard) dashboardCard.classList.remove("hidden");
      if (maintenanceFormCard) maintenanceFormCard.classList.add("hidden");
      if (maintenanceTableCard) maintenanceTableCard.classList.add("hidden");
    };
  }
  if (backFromTableBtn) {
    backFromTableBtn.onclick = function() {
      if (dashboardCard) dashboardCard.classList.remove("hidden");
      if (maintenanceFormCard) maintenanceFormCard.classList.add("hidden");
      if (maintenanceTableCard) maintenanceTableCard.classList.add("hidden");
    };
  }

  const maintenanceForm = document.getElementById("maintenance-form");
  if (maintenanceForm) {
    maintenanceForm.onsubmit = async function(e) {
      e.preventDefault();
      
      // Get form values
      const monthInput = document.getElementById("main_month").value; // Format: "2025-09"
      const dateInput = document.getElementById("main_date").value;
      const amountInput = document.getElementById("main_amount").value;
      const paidByInput = document.getElementById("paid_by").value;
      const ownerNameInput = document.getElementById("owner_name").value;
      
      // Validate required fields
      if (!monthInput || !dateInput || !amountInput || !paidByInput || !ownerNameInput) {
        document.getElementById("maintenance-message").innerText = "Please fill in all fields.";
        return;
      }
      
      // Extract year and month name from monthInput (format: "2025-09")
      const [yearStr, monthNumStr] = monthInput.split('-');
      const year = parseInt(yearStr);
      const monthName = new Date(monthInput + "-01").toLocaleString('default', { month: 'long' });
      
      // Validate year
      if (isNaN(year) || year < 2020 || year > 2030) {
        document.getElementById("maintenance-message").innerText = "Please enter a valid year between 2020-2030.";
        return;
      }
      
      const data = {
        date: dateInput,
        month: monthName,
        year: year,
        amount: parseFloat(amountInput),
        paid_by: parseInt(paidByInput),
        owner_name: ownerNameInput
      };
      
      console.log("Submitting maintenance data:", data);
      
      try {
        const response = await fetch(`/income/?username=${encodeURIComponent(username)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(data)
        });
        console.log(JSON.stringify(data));
        const result = await response.json();
        if (response.ok) {
          document.getElementById("maintenance-message").innerText = "Maintenance added!";
          maintenanceForm.reset();
        } else {
          document.getElementById("maintenance-message").innerText = result.detail || "Failed to add maintenance.";
        }
      } catch (error) {
        console.error("Error submitting maintenance:", error);
        document.getElementById("maintenance-message").innerText = "Error adding maintenance.";
      }
    };
  }

  async function loadMaintenance(year = null, month = null) {
    const tbody = document.getElementById("maintenance-body");
    if (!tbody) return;
    tbody.innerHTML = "";
    try {
      // Build URL with optional filters
      let url = `/income/?username=${encodeURIComponent(username)}`;
      if (year) url += `&year=${encodeURIComponent(year)}`;
      if (month) url += `&month=${encodeURIComponent(month)}`;
      
      const response = await fetch(url, { credentials: "include" });
      const maintenance = await response.json();

      maintenance.forEach(main => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${main.owner_name || ''}</td>
          <td>${main.date}</td>
          <td>${main.month}</td>
          <td>${main.year}</td>
          <td>${main.amount}</td>
          <td>${main.paid_by}</td>
          <td><button onclick="downloadReceipt(${main.id})" class="download-btn">Download Receipt</button></td>
        `;
        tbody.appendChild(tr);
      });
    } catch {
      tbody.innerHTML = "<tr><td colspan='7'>Failed to load maintenance records.</td></tr>";
    }
  }

  function showFilterMessage() {
    const tbody = document.getElementById("maintenance-body");
    if (!tbody) return;
    tbody.innerHTML = "<tr><td colspan='7' style='text-align: center; padding: 20px; color: #666;'>Please select filters above and click 'Apply Filter' to view maintenance records.</td></tr>";
  }
  var maintenanceId = userid;

  // Filter functionality
  const applyFiltersBtn = document.getElementById("apply-filters");
  const clearFiltersBtn = document.getElementById("clear-filters");
  
  if (applyFiltersBtn) {
    applyFiltersBtn.onclick = function() {
      const selectedYear = document.getElementById("filter-year").value || null;
      const selectedMonth = document.getElementById("filter-month").value || null;
      
      // Require at least one filter to be selected
      if (!selectedYear && !selectedMonth) {
        alert("Please select at least Year or Month to filter records.");
        return;
      }
      
      loadMaintenance(selectedYear, selectedMonth);
    };
  }
  
  if (clearFiltersBtn) {
    clearFiltersBtn.onclick = function() {
      document.getElementById("filter-year").value = "";
      document.getElementById("filter-month").value = "";
      showFilterMessage(); // Show the filter message instead of loading all records
    };
  }

  // Make downloadReceipt function global so HTML buttons can access it
  window.downloadReceipt = async function(maintenanceId){
    try{
      const response = await fetch(`/income/${maintenanceId}/receipt?username=${encodeURIComponent(username)}`, {
        method: "GET",
        credentials: "include"
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `receipt_${maintenanceId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error("Failed to download receipt.");
        alert("Failed to download receipt. Please try again.");
      }
    } catch (error) {
      console.error("Error downloading receipt:", error);
      alert("Error downloading receipt. Please try again.");
    }
  }

  document.getElementById('logoutBtn').onclick = async function() {
      await fetch('/logout', { method: 'POST', credentials: 'include' });
      window.location.href = '/';
  };
});

