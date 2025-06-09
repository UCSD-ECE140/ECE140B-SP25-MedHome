const { jsPDF } = window.jspdf;

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

document.querySelector(".export-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const title = document.getElementById("export-title").value;

    const currentUrl = window.location.href;
    const username = currentUrl.split('/').pop();

    try {
        const response = await fetch(`/export/user/${username}`, {
            method: "POST"
        });

        if (!response.ok) {
            alert("Failed to export report. Please try again later.");
            console.error("Export failed with status:", response.status);
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `${title || "health_report"}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (err) {
        console.error("Export failed:", err);
        alert("An error occurred while exporting the report.");
    }
});