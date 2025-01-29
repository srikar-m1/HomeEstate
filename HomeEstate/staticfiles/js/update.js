const updateUserProfile = async () => {
  const firstName = document.getElementById('first_name').value;
  const lastName = document.getElementById('last_name').value;
  const email = document.getElementById('email').value;

  const token = localStorage.getItem('knox_token');
  if (!token) {
    alert('You must be logged in to update your profile.');
    return;
  }

  try {
    const userId = document.getElementById('user_id').value;
    const response = await fetch(`/api/update/${userId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`,
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email
      }),
    });

    const data = await response.json();

    if (response.ok) {
      alert('Profile updated successfully!');
      window.location.href = '/';  // Redirect to   home
    } else {
      alert('Update failed: ' + data.errors);
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    alert('An error occurred while updating the profile.');
  }
};

// Target the update profile link
document.getElementById('updateProfileLink').addEventListener('click', updateUserProfile);
