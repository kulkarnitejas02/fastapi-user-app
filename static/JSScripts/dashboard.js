document.addEventListener("DOMContentLoaded", function() {
  async function getUserInfo() {
    try {
      const response = await fetch("/me");
      if (response.ok) {
        const user = await response.json();
        document.getElementById("welcome").innerText = `Welcome, ${user.name || "User"}!`;
        document.getElementById("role").innerText = `Role: ${user.role || "guest"}`;
      }
    } catch {}
  }
  getUserInfo();

  // Navigation for Expenses and Income
  const expensesBtn = document.querySelector("a[href='/dashboard/expenses']");
  const incomeBtn = document.querySelector("a[href='/dashboard/income']");
  if (expensesBtn) {
    expensesBtn.onclick = function(e) {
      e.preventDefault();
      window.location.href = "/dashboard/expenses";
    };
  }
  if (incomeBtn) {
    incomeBtn.onclick = function(e) {
      e.preventDefault();
      window.location.href = "/dashboard/income";
    };
  }

  document.getElementById('logoutBtn').onclick = async function() {
      await fetch('/auth/logout', { method: 'POST', credentials: 'include' });
      window.location.href = '/';
  };
});

