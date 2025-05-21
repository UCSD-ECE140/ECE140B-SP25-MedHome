// Get the current URL of the webpage
const currentUrl = window.location.href;

username = currentUrl.split('/').pop();

// Get the elements by their classname and set their href attributes
profileLink = document.querySelector('.profile-link');
profileLink.href = `/profile/user/${username}`;

dashboardLink = document.querySelector('.dashboard-link');
dashboardLink.href = `/dashboard/user/${username}`;

// grab username and set it in the profile header
const profileHeader = document.querySelector('#welcome-message');
profileHeader.innerHTML = 'Welcome, ' + username + '!';

const logoutForm = document.querySelector('.logout-form');
logoutForm.addEventListener('click', function (event) {
    event.preventDefault(); // Prevent the default form submission
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}) // Send an empty object as the body
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/'; // Redirect to the home page on success
        } else {
            console.error('Logout failed:', response.statusText);
        }
    })
    .catch(error => console.error('Error:', error));
});

document.querySelector(".export-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const title = document.getElementById("export-title").value;
    const selected = Array.from(document.querySelectorAll(".data-list input:checked")).map(input => input.name);
    alert(`Exporting: ${selected.join(", ")}\nTitle: ${title}`);
    // You can replace this alert with an actual fetch() or form submission
});