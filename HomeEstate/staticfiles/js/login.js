// login.js
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault(); // Prevent default form submission

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  try {
    // Send POST request to login API
    const response = await fetch('/accounts/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      const data = await response.json();
      // Store the token in localStorage
      if (data.token) {
        localStorage.setItem('knox_token', data.token);
        // Redirect to the home page
        window.location.href = '/'; // Redirect after successful login
      } else {
        console.error("Token not found in response");
      }
    } else {
      alert('Login failed');
    }
  } catch (error) {
    console.error('Error during login:', error);
  }
});
