const registerUser = async () => {
  const firstName = document.getElementById('first_name').value;
  const lastName = document.getElementById('last_name').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch('/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password
      }),
    });

    const data = await response.json();

    if (response.ok) {
      // Redirect to login page after successful registration
      window.location.href = '/';  // This will send the user to the login page
    } else {
      alert('Registration failed: ' + data.errors);
    }
  } catch (error) {
    console.error('Error during registration:', error);
    alert('An error occurred during registration.');
  }
};

// Attach event listener to form submission
document.getElementById('registerForm').addEventListener('submit', (event) => {
  event.preventDefault();  // Prevent default form submission
  registerUser();  // Call registerUser function
});
