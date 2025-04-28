// Get the current URL of the webpage
const currentUrl = window.location.href;

username = currentUrl.split('/').pop();

// Get the elements by their classname and set their href attributes
dashboardLink = document.querySelector('.dashboard-link');
dashboardLink.href = `/dashboard/user/${username}`;

exportLink = document.querySelector('.export-link');
exportLink.href = `/export/user/${username}`;

usernameDisplay = document.querySelector('#user-name');
usernameDisplay.innerHTML = `User: ${username}`;

// grab username and set it in the profile header
const profileHeader = document.querySelector('#welcome-message');
profileHeader.innerHTML = 'Welcome, ' + username + '!';