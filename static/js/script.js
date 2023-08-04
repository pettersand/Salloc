// Sorting of overview table
function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("myTable");
    if (!table) return; // If the table doesn't exist, exit the function
    switching = true;
    // Set the sorting direction to descending:
    dir = "desc"; 
    // Remove the sort symbol from all columns:
    for (i = 0; i < 5; i++) {
      table.rows[0].getElementsByTagName("TH")[i].innerHTML = table.rows[0].getElementsByTagName("TH")[i].innerHTML.replace(" ▲", "").replace(" ▼", "");
    }
    while (switching) {
      switching = false;
      rows = table.rows;
      for (i = 1; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("TD")[n];
        y = rows[i + 1].getElementsByTagName("TD")[n];
        if (dir == "desc") {
          if (n === 3) { // if it's the progress bar column
            var xVal = x.getElementsByTagName("progress")[0].value;
            var xMax = x.getElementsByTagName("progress")[0].max;
            var yVal = y.getElementsByTagName("progress")[0].value;
            var yMax = y.getElementsByTagName("progress")[0].max;
            if ((xVal / xMax) < (yVal / yMax)) {
              shouldSwitch = true;
              break;
            }
          } else if (isNaN(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) { // if it's a string
            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
              shouldSwitch = true;
              break;
            }
          } else { // if it's a number
            if (Number(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', '')) < Number(y.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) {
              shouldSwitch = true;
              break;
            }
          }
        } else if (dir == "asc") {
          if (n === 3) { // if it's the progress bar column
            var xVal = x.getElementsByTagName("progress")[0].value;
            var xMax = x.getElementsByTagName("progress")[0].max;
            var yVal = y.getElementsByTagName("progress")[0].value;
            var yMax = y.getElementsByTagName("progress")[0].max;
            if ((xVal / xMax) > (yVal / yMax)) {
              shouldSwitch = true;
              break;
            }
          } else if (isNaN(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) { // if it's a string
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
              shouldSwitch = true;
              break;
            }
          } else { // if it's a number
            if (Number(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', '')) > Number(y.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''))) {
              shouldSwitch = true;
              break;
            }
          }
        }
      }
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount ++;      
      } else {
        if (switchcount == 0 && dir == "desc") {
          dir = "asc";
          switching = true;
        }
      }
    }
    // Add the sort symbol to the sorted column:
    if (dir == "asc") {
      table.rows[0].getElementsByTagName("TH")[n].innerHTML += " ▼";
    } else if (dir == "desc") {
      table.rows[0].getElementsByTagName("TH")[n].innerHTML += " ▲";
    }
  }

// MODAL JS

window.onload = function() {
    // Get the modal
    var modal = document.getElementById("myModal");
    if (!modal) return;  // If there's no modal on the page, stop the script

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    if (span) {
        span.onclick = function() {
            modal.style.display = "none";
        }
    }

    var registerButton = document.getElementById("registerButton");
    if (registerButton) {
        registerButton.onclick = function(event) {
            event.preventDefault();  // Prevent the form from being submitted
            modal.style.display = "block";  // Display the modal
        }
    }

    // Handle consent checkboxes
    var consentCheckbox = document.getElementById("consent");
    var noConsentCheckbox = document.getElementById("noConsent");
    var consentField = document.getElementById("consentField"); // Make sure this is the ID of the hidden input field in the form

    if (consentCheckbox && noConsentCheckbox) {
        consentCheckbox.onclick = function() {
            if (consentCheckbox.checked) {
                noConsentCheckbox.checked = false;
            }
        }

        noConsentCheckbox.onclick = function() {
            if (noConsentCheckbox.checked) {
                consentCheckbox.checked = false;
            }
        }
    }

    var continueButton = document.getElementById("continueButton");
    if (continueButton && consentField) {
        continueButton.onclick = function() {
            if (consentCheckbox.checked) {
                consentField.value = 'yes';
            } else if (noConsentCheckbox.checked) {
                consentField.value = 'no';
            }
            // Submit the form
            var form = document.getElementById("registerForm");
            if (form) {
                form.submit();
            }
        }
    }
}


// Function to close the modal
function closeModal() {
  var modal = document.getElementById("myModal");
  modal.style.display = "none";
}
