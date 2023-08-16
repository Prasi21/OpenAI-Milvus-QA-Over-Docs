// Sends the state of all the checkboxes to the backend when any of them are updated
document.addEventListener("DOMContentLoaded", function() {
    // Get references to the checkboxes
    var partitionNamesElement = document.getElementById("partitionNames");
    var partitionNames = JSON.parse(partitionNamesElement.textContent);
    var checkboxes = {};

    partitionNames.forEach(function(partitionName) {
        var checkboxId = partitionName;
        checkboxes[partitionName] = document.getElementById(checkboxId);

        // Restore checkbox state from localStorage if available
        var storedState = localStorage.getItem(checkboxId);
        if (storedState) {
            checkboxId[partitionName].checked = (storedState === 'true');
        }

        checkboxes[partitionName].addEventListener("change", function() {
            // Update localStorage with checkbox state
            localStorage.setItem(checkboxId, checkboxes[partitionName].checked);
            updateServer();
        });    

    });

    function updateServer() {
        // Create an array to store selected partition names
        var selectedPartitions = [];

        // Check the state of each checkbox and add selected partitions to the array
        partitionNames.forEach(function(partitionName) {
            if (checkboxes[partitionName].checked) {
                selectedPartitions.push(partitionName);
            }
        });

        // Send the selected partitions to the server using fetch or AJAX
        fetch("/update_partitions", {
            method: "POST",
            body: JSON.stringify(selectedPartitions),
            headers: {
                "Content-Type": "application/json"
            }
        });
    }
});

console.log(document.readyState)