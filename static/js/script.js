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
// Function to show warning popup
function showWarningPopup(modalId, message, action, warningName) {
    // Get the modal
    var modal = document.getElementById(modalId);
    if (!modal) return;  // If there's no modal on the page, stop the script

    // Set the warning message
    var warningMessageElement = document.getElementById("warningMessage");
    if (warningMessageElement) {
        warningMessageElement.textContent = message;
    }

    // Handle the "Cancel" button
    var cancelButton = document.getElementById("cancelButton");
    if (cancelButton) {
        cancelButton.onclick = function() {
            modal.style.display = "none";
        }
    }

    // Handle the "Accept" button
    var acceptButton = document.getElementById("acceptButton");
    if (acceptButton) {
        acceptButton.onclick = function() {
            modal.style.display = "none";
            action();
        }
    }

    // Handle the checkboxes
    var ignoreThisCheckbox = document.getElementById("ignoreThisCheckbox");
    var ignoreAllCheckbox = document.getElementById("ignoreAllCheckbox");
    if (ignoreThisCheckbox && ignoreAllCheckbox) {
        ignoreThisCheckbox.onclick = function() {
            if (ignoreThisCheckbox.checked) {
                ignoreAllCheckbox.checked = false;
                // Update the user's cookie preferences
                document.cookie = warningName + "=true; path=/";
            }
        }
        ignoreAllCheckbox.onclick = function() {
            if (ignoreAllCheckbox.checked) {
                ignoreThisCheckbox.checked = false;
                // Update the user's cookie preferences
                document.cookie = "ignoreAllWarnings=true; path=/";
            }
        }
    }

    // Show the modal
    modal.style.display = "block";
}

// Function to check the user's cookie preferences
function checkCookiePreferences(modalId, message, action, warningName) {
    // Check the user's cookies
    var consent = document.cookie.split('; ').find(row => row.startsWith('consent='));
    var ignoreThisWarning = document.cookie.split('; ').find(row => row.startsWith(warningName + '='));
    var ignoreAllWarnings = document.cookie.split('; ').find(row => row.startsWith('ignoreAllWarnings='));

    // If the user has not given consent, show the warning popup
    if (!consent) {
        showWarningPopup(modalId, message, action, warningName);
    } else if (!ignoreThisWarning && !ignoreAllWarnings) {
        // If the user has given consent but has not opted to ignore this warning or all warnings, show the warning popup
        showWarningPopup(modalId, message, action, warningName);
    } else {
        // If the user has given consent and has opted to ignore this warning or all warnings, perform the action
        action();
    }
}

// Attach the checkCookiePreferences function to the "Remove Post" button
var removePostButton = document.getElementById("removePostButton");
if (removePostButton) {
    removePostButton.onclick = function(event) {
        event.preventDefault();  // Prevent the form from being submitted
        checkCookiePreferences(
            "warningModal",  // The ID of the modal to display
            "Warning: Removing a post may affect certain aspects of the program.",
            function() {
                // Action to perform if the user accepts the warning
                document.getElementById("removePostForm").submit();
            },
            "ignoreRemovePostWarning"  // The name of the warning
        );
    }
}

// Function to close the modal
function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    if (modal) {  // If the modal exists on the page
      modal.style.display = "none";
    }
  }

// Get the modal
var modal = document.getElementById("myModal");
if (modal) {  // If there's no modal on the page, stop the script

// Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    if (span) {
        span.onclick = function() {
            closeModal("myModal");  // Close the modal
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
    var consentField = document.getElementById("consentField"); 

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

console.log("CookiePref Loaded");