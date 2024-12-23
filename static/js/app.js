document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const address = document.getElementById('address').value.trim();
  const status = document.getElementById('status');

  if (!address) {
    status.textContent = 'Please enter a valid address.';
    return;
  }

  status.textContent = 'Connecting to the blockchain...';

  try {
    const response = await fetch('http://localhost:8765', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address }),
    });

    if (response.ok) {
      const result = await response.json();
      status.textContent = `Welcome, Validator: ${result.validator_id}`;
      status.style.color = 'lightgreen';
    } else {
      status.textContent = 'Connection failed. Try again.';
      status.style.color = 'red';
    }
  } catch (error) {
    console.error('Error:', error);
    status.textContent = 'Network error. Is the server running?';
    status.style.color = 'red';
  }
});
