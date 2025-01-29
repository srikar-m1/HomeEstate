document.getElementById('logoutButton').addEventListener('click', async function(e) {
    // Prevent any default action (in case it's in a form or there are default behaviors)
    e.preventDefault();

    const token = localStorage.getItem('knox_token');

    if (!token) {
        alert('You are not logged in.');
        return;
    }

    try {
        const response = await fetch('accounts/api/logout/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`  // Send the Knox token in the Authorization header
            },
        });

        if (response.ok) {
            // Successfully logged out, clear the token from localStorage
            localStorage.removeItem('knox_token');

            // Redirect to the login page or home page after logout
            window.location.href = '/';
        } else {
            alert('An error occurred while logging out. Please try again.');
        }
    } catch (error) {
        console.error('Error logging out:', error);
        alert('An error occurred while logging out.');
    }
});
