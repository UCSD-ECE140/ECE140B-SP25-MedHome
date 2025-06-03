// Get the current URL of the webpage
const currentUrl = window.location.href;

username = currentUrl.split('/').pop();

// Get the elements by their classname and set their href attributes
profileLink = document.querySelector('.profile-link');
profileLink.href = `/profile/user/${username}`;

exportLink = document.querySelector('.export-link');
exportLink.href = `/export/user/${username}`;

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

let charts = {};

document.addEventListener("DOMContentLoaded", function () {
  const analysisButton = document.getElementById("analysis-button"); 
  const analysisResponse = document.getElementById("analysis-response"); 
  analysisButton.addEventListener("click", async function(theEvent) {
    // alert("Click test !"); 
    theEvent.preventDefault();  
    theData = await getData(); 
    // console.log(theData["theResponse"]); 
    analysisResponse.textContent = theData["theResponse"]; 
  }); 


  // Attach click handlers to all metric buttons
  document.querySelectorAll(".metric-card").forEach(card => {
    const type = card.getAttribute("data-type");
    const button = card.querySelector(".metric-button");
    const canvas = card.querySelector("canvas");

    if (button && canvas) {
      button.addEventListener("click", () => {
        const chartId = canvas.id;
        
        if (canvas.style.display === "block") {
          // Hide the chart and destroy it
          canvas.style.display = "none";
          button.textContent = "Show graph";
          if (charts[chartId]) {
            charts[chartId].destroy();
            delete charts[chartId];

            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Click the button to toggle visibility
            button.click();
          }
        } else {
          // Show and draw the chart
          canvas.style.display = "block";
          button.textContent = "Hide graph";
          renderChart(chartId, type);
        }
      });
    }
  });
});

async function getData() {
    const theResponse = await fetch(`/dashboard/user/${username}/data`); 
    const theData = await theResponse.json(); 
    
    return theData;  
}

// Chart rendering function
function renderChart(canvasId, type) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  let label = "";
  let data = [];
  let labels = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"];

  switch (type) {
    case "heartrate":
      label = "Heart Rate (bpm)";
      data = [72, 75, 70, 78, 74, 76, 73];
      break;
    case "bp":
      label = "Blood Pressure";
      data = [120, 122, 118, 121, 119, 123, 120];
      break;
    case "weight":
      label = "Weight (lbs)";
      data = [150, 149, 151, 148, 150, 149, 152];
      break;
    default:
      label = "Unknown Metric";
  }

  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: data,
        fill: false,
        borderColor: 'blue',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });

  charts[canvasId] = chart;
}
