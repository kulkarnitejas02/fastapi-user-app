document.addEventListener("DOMContentLoaded", function() {
  let name = "User";
  let role = "guest";
  let username = "";
  let userid = 0;
  console.log("expense.js loaded"); 
  async function getUserInfo() {
    try {
      const response = await fetch("/me");
      if (response.ok) {
        const user = await response.json();
        name = user.name || "User";
        role = user.role || "guest";
        username = user.username || "";
        userid = user.userid || 0;
        name = user.name || "User";
      }
      console.log(name);
    } catch {}
    document.getElementById("welcome").innerText = `Welcome, ${name}!`;
    document.getElementById("role").innerText = `Role: ${role}`;
  }
  getUserInfo();

  // Expense page logic
  document.getElementById("dashboard-card").classList.remove("hidden");
  document.getElementById("expense-form-card").classList.add("hidden");
  document.getElementById("expenses-table-card").classList.add("hidden");

  document.getElementById("add-expense-btn").onclick = function() {
    console.log("Add Expenses clicked");
    if (role === "secretary" || role === "treasurer" || role === "member") {
      document.getElementById("dashboard-card").classList.add("hidden");
      document.getElementById("expense-form-card").classList.remove("hidden");
      document.getElementById("expenses-table-card").classList.add("hidden");
    } else {
      alert("You do not have permission to add expenses.");
    }
  };
  document.getElementById("view-expense-btn").onclick = function() {
    document.getElementById("dashboard-card").classList.add("hidden");
    document.getElementById("expense-form-card").classList.add("hidden");
    document.getElementById("expenses-table-card").classList.remove("hidden");
    loadExpenses();
  };
  document.getElementById("back-from-form-btn").onclick = function() {
    document.getElementById("dashboard-card").classList.remove("hidden");
    document.getElementById("expense-form-card").classList.add("hidden");
    document.getElementById("expenses-table-card").classList.add("hidden");
  };
  document.getElementById("back-from-table-btn").onclick = function() {
    document.getElementById("dashboard-card").classList.remove("hidden");
    document.getElementById("expense-form-card").classList.add("hidden");
    document.getElementById("expenses-table-card").classList.add("hidden");
  };

  async function loadUsers() {
    try {
      const response = await fetch("/users");
      const users = await response.json();
      const select = document.getElementById("exp_paid_by");
      select.innerHTML = '<option value="">Select Paid By</option>';
      users.forEach(user => {
        const option = document.createElement("option");
        option.value = user.flat_number;
        option.text = user.flat_number;
        select.appendChild(option);
      });
      console.log(option);
    } catch {}
  }
  loadUsers();

  const expenseForm = document.getElementById("expense-form");
  if (expenseForm) {
    expenseForm.onsubmit = async function(e) {
      e.preventDefault();
      const monthInput = document.getElementById("exp_month").value;
      const monthName = new Date(monthInput + "-01").toLocaleString('default', { month: 'long' });

      const [yearStr, monthNumStr] = monthInput.split("-");
      const year = parseInt(yearStr);
      //validate year
      if(isNaN(year) || year < 2000 || year > 2100) {
        document.getElementById("expense-message").innerText = "Please enter a valid year.";
        return;
      }

      const data = {
        expense_name: document.getElementById("exp_name").value,
        date: document.getElementById("exp_date").value,
        month: monthName,
        year: year,
        description: document.getElementById("exp_desc").value,
        amount: parseFloat(document.getElementById("exp_amount").value),
        paid_by: parseInt(document.getElementById("exp_paid_by").value),
        created_by: name
      };
      try {
        const response = await fetch(`/expenses/?username=${encodeURIComponent(username)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(data)
        });
        console.log(JSON.stringify(data));
        const result = await response.json();
        if (response.ok) {
          document.getElementById("expense-message").innerText = "Expense added!";
          expenseForm.reset();
        } else {
          document.getElementById("expense-message").innerText = result.detail || "Failed to add expense.";
        }
      } catch {
        document.getElementById("expense-message").innerText = "Error adding expense.";
      }
    };
  }

  async function loadExpenses(year = null, month = null) {
    const tbody = document.getElementById("expenses-body");
    tbody.innerHTML = "";

    try {

      let url = `/expenses/?username=${encodeURIComponent(username)}`;
      if (year) url += `&year=${encodeURIComponent(year)}`;
      if (month) url += `&month=${encodeURIComponent(month)}`;
      

      const response = await fetch(url, { credentials: "include" });
      const expenses = await response.json();
      expenses.forEach(exp => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${exp.date}</td>
          <td>${exp.month}</td>
          <td>${exp.description}</td>
          <td>${exp.amount}</td>
          <td>${exp.paid_by}</td>
          <td>${exp.created_by}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch {
      tbody.innerHTML = "<tr><td colspan='4'>Failed to load expenses.</td></tr>";
    }
  }


  document.getElementById('logoutBtn').onclick = async function() {
      await fetch('/auth/logout', { method: 'POST', credentials: 'include' });
      window.location.href = '/';
  };
});

