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

async function getData() {
    const theResponse = await fetch(`/dashboard/user/${username}/data`); 
    const theData = await theResponse.json(); 
    
    return theData;  
}

document.addEventListener("DOMContentLoaded", async function () {
  const analysisButton = document.getElementById("analysis-button"); 
  const analysisResponse = document.getElementById("analysis-response"); 
  analysisButton.addEventListener("click", async function(theEvent) {
    // alert("Click test !"); 
    theEvent.preventDefault();  
    theData = await getData(); 
    console.log(theData); 
    analysisResponse.textContent = theData["theResponse"]; 
  }); 


  // Attach click handlers to all metric buttons
  document.querySelectorAll(".metric-card").forEach(card => {
    const type = card.getAttribute("data-type");
    const button = card.querySelector(".metric-button");
    const canvas = card.querySelector("canvas");

    if (button && canvas) {
      button.addEventListener("click", async () => {
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
          await renderChart(chartId, type);
        }
      });
    }
  });

  // Initial rendering of charts by clicking the buttons
  document.querySelectorAll(".metric-button").forEach(button => {
    button.click();
  });
});

// Chart rendering function
async function renderChart(canvasId, type) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  // ✅ Use your structured backend data
  const response = await fetch(`/dashboard/user/${username}/data`);
  const userData = await response.json();

  if (type === "bp") {
    const systolic = userData["systolic"];
    const diastolic = userData["diastolic"];

    const systolicNotValid = !systolic || systolic.length == 0;
    const diastolicNotValid = !diastolic || diastolic.length == 0;

    if (systolicNotValid || diastolicNotValid) {
      console.warn("Blood pressure data missing or empty");
      canvas.style.display = "block";
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.font = "16px Arial";
      ctx.fillStyle = "gray";
      ctx.textAlign = "center";
      ctx.fillText("Not enough data to generate chart", canvas.width / 2, canvas.height / 2);

      const button = document.querySelector(`button[data-type="${type}"]`);
      if (button) button.textContent = "Show graph (no data)";
      return;
    }
  }


  if (type !== "bp" && (!userData || !userData[type] || userData[type].length === 0)) {
    console.warn(`Not enough data to display chart for: ${type}`);
    canvas.style.display = "block";
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = "16px Arial";
    ctx.fillStyle = "gray";
    ctx.textAlign = "center";
    ctx.fillText("Not enough data to generate chart", canvas.width / 2, canvas.height / 2);

    const button = document.querySelector(`button[data-type="${type}"]`);
    if (button) button.textContent = "Show graph (no data)";
    return;
  }

  let label = "";
  let data = [];
  let labels = userData.dates;  // use actual date labels from backend

  switch (type) {
  case "bpm":
    label = "Heart Rate (bpm)";
    data = [...userData.bpm];
    break;
  case "bp":
    label = "Blood Pressure (mmHg)";
    data = {
      systolic: [...userData.systolic],
      diastolic: [...userData.diastolic]
    };
    break;
  case "weight":
    label = "Weight (lbs)";
    data = [...userData.weight];
    break;
  case "spo2":
    label = "Oxygen Saturation (%)";
    data = [...userData.spo2];
    break;
  default:
    label = "Unknown Metric";
}

  // Convert BP strings to show as text if needed, or just graph systolic
  const numericData = type === "bp" ? userData.systolic : data;

  const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: labels,
    datasets: type === "bp" ? [
      {
        label: "Systolic",
        data: data.systolic,
        borderColor: 'red',
        fill: false,
        tension: 0.1
      },
      {
        label: "Diastolic",
        data: data.diastolic,
        borderColor: 'blue',
        fill: false,
        tension: 0.1
      }
    ] : [{
      label: label,
      data: data,
      borderColor: 'blue',
      fill: false,
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
