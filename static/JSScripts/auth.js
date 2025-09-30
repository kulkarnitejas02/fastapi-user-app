// Helper function to show a message
function showMessage(message, type = 'success') {
  const display = document.getElementById('message-display');
  display.textContent = message;
  display.className = 'mt-4 p-4 rounded-lg text-sm text-center font-medium transition-all duration-300';
  if (type === 'success') {
    display.classList.add('bg-green-100', 'text-green-800');
  } else if (type === 'error') {
    display.classList.add('bg-red-100', 'text-red-800');
  }
  display.style.opacity = '1';
  setTimeout(() => {
    display.style.opacity = '0';
  }, 5000);
}

// Navigation functions
function showRegister() {
  document.getElementById('login-view').classList.add('hidden');
  document.getElementById('register-view').classList.remove('hidden');
  document.getElementById('forget-password-view').classList.add('hidden');
  document.getElementById('message-display').textContent = '';
}

function showLogin() {
  document.getElementById('login-view').classList.remove('hidden');
  document.getElementById('register-view').classList.add('hidden');
  document.getElementById('forget-password-view').classList.add('hidden');
  document.getElementById('message-display').textContent = '';
}

function showForgetPassword() {
  document.getElementById('login-view').classList.add('hidden');
  document.getElementById('register-view').classList.add('hidden');
  document.getElementById('forget-password-view').classList.remove('hidden');
  document.getElementById('message-display').textContent = '';
  console.log("Forget Password Clicked");
}

// API handlers
async function handleForgetPassword() {
  const username = document.getElementById("fp_username").value;
  const contactId = document.getElementById("fp_contact").value;
  const newPassword = document.getElementById("fp_new_password").value;
  const confirmPassword = document.getElementById("fp_confirm_password").value;

  // Basic validation
  if (!username || !contactId || !newPassword || !confirmPassword) {
    showMessage("Please fill in all fields", 'error');
    return;
  }

  if (newPassword !== confirmPassword) {
    showMessage("Passwords do not match", 'error');
    return;
  }

  if (newPassword.length < 4) {
    showMessage("Password must be at least 4 characters long", 'error');
    return;
  }

  const data = {
    username: username,
    contact_id: contactId,
    new_password: newPassword
  };

  try {
    const response = await fetch("/reset-password", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    if (response.ok) {
      showMessage("Password reset successful! You can now login with your new password.", 'success');
      // Clear the form
      document.getElementById("fp_username").value = '';
      document.getElementById("fp_contact").value = '';
      document.getElementById("fp_new_password").value = '';
      document.getElementById("fp_confirm_password").value = '';
      // Switch to login view after 2 seconds
      setTimeout(showLogin, 2000);
    } else {
      showMessage(result.detail || "Password reset failed", 'error');
    }
  } catch (error) {
    showMessage("An error occurred. Please try again later.", 'error');
  }
}

async function handleRegister() {
  const data = {
    username: document.getElementById("reg_username").value,
    password: document.getElementById("reg_password").value,
    name: document.getElementById("reg_name").value,
    flat_number: document.getElementById("reg_flat").value,
    contact_id: document.getElementById("reg_contact").value,
    role: document.querySelector('input[name="reg_role"]:checked').value
  };

  try {
    const response = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    if (response.ok) {
      showMessage(result.message, 'success');
      // Switch to login view on successful registration
      setTimeout(showLogin, 2000);
    } else {
      showMessage(result.detail || "Registration failed", 'error');
    }
  } catch (error) {
    showMessage("An error occurred. Please try again later.", 'error');
  }
}

async function handleLogin() {
  const data = {
    username: document.getElementById("login_username").value,
    password: document.getElementById("login_password").value
  };

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    if (response.ok) {
      showMessage(result.message, 'success');
      // Redirect to dashboard
      window.location.href = `/dashboard`;
    } else {
      showMessage(result.detail || "Login failed", 'error');
    }
  } catch (error) {
    showMessage("An error occurred. Please try again later.", 'error');
  }
}

