document.addEventListener("DOMContentLoaded", function () {
    const updateInterval = 100;  // Update every 2 seconds

    function updateProgressBars() {
        fetch('/task_status')
            .then(response => response.json())
            .then(data => {
                for (const [taskId, taskData] of Object.entries(data)) {
                    console.log(taskId, taskData);
                    const progressBarFrame = document.getElementById(`progress-bar-frame-${taskId}`);
                    const progressBar = document.getElementById(`progress-bar-${taskId}`);
                    const statusNumber = document.getElementById(`status-number-${taskId}`);
                    const statusValue = taskData.result;
                    // Update the progress bar and status number
                    progressBar.style.width = statusValue / 150 * 100 + "%";

                    if (statusValue == 150) {	
                        statusNumber.textContent = "done";
                        statusNumber.style.color = "green";
                        statusNumber.style.text = "green";
                        progressBarFrame.style.display = "none";
                    }
                    else if (statusValue == 0){
                        statusNumber.textContent = "pending";
                        statusNumber.style.color = "grey";
                        progressBarFrame.style.display = "none";
                    } else {
                        statusNumber.textContent = Math.floor(statusValue / 150 * 100) + "%";
                        statusNumber.style.color = "";
                        progressBarFrame.style.display = "";
                    }
                }
            })
            .catch(error => console.error('Error fetching task status:', error));
    }

    // Initial update
    updateProgressBars();
    
    // Set an interval to update progress bars
    setInterval(updateProgressBars, updateInterval);
});

