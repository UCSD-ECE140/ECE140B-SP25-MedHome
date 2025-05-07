// Get the current URL of the webpage
const currentUrl = window.location.href;

username = currentUrl.split('/').pop();

// Get the elements by their classname and set their href attributes
profileLink = document.querySelector('.profile-link');
profileLink.href = `/profile/user/${username}`;

exportLink = document.querySelector('.export-link');
exportLink.href = `/export/user/${username}`;

const profileHeader = document.querySelector('#welcome-message');
profileHeader.innerHTML = 'Welcome, ' + username + '!';

let charts = [];

async function createChart(sensorType, canvasId, label, color) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  // temp data for testing
  const data = [{x: new Date("2023-01-01"), y: 2}, {x: new Date("2023-01-02"), y: 3}, {x: new Date("2023-01-03"), y: 4}];

  console.log("First fetch: " + JSON.stringify(data));
  charts.push(new Chart(ctx, {
      type: 'line',
      data: {
datasets: [{
              label: label,
              data: data,
              borderColor: color,
              fill: false
          }]
      },
      options: {
          responsive: true,
          plugins: {
              title: {
                  display: true,
                  text: `${label}`
              }
          },
          scales: {
              x: {
                  type: 'time',
                  time: {
                      unit: 'day'
                  },
                  title: {
                      display: true,
                      text: 'Date'
                  }
              },
              y: {
                  beginAtZero: true,
                  title: {
                      display: true,
                      text: 'Value'
                  }
              }
          }
      }
  }));
}
document.addEventListener("DOMContentLoaded", () => {
  createChart("Heartrate", "heartrateChart", "Heartrate Over Time", "red");
  createChart("BloodPressure", "bloodPressureChart", "Blood Pressure Over Time", "blue");
  createChart("Weight", "weightChart", "Weight Over Time", "green");
  console.log(charts);
});