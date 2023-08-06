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

    // Check the user's cookies
    var consent = document.cookie.split('; ').find(row => row.startsWith('consent='));

    // Get the checkbox container
    var checkboxContainer = document.getElementById("checkboxContainer");

    // Handle the checkboxes
    var ignoreThisCheckbox = document.getElementById("ignoreThisCheckbox");
    var ignoreAllCheckbox = document.getElementById("ignoreAllCheckbox");
    if (ignoreThisCheckbox && ignoreAllCheckbox && checkboxContainer) {
        // If the user has given consent, show the checkboxes and handle their clicks
        if (consent) {
            checkboxContainer.style.display = "block";
            ignoreThisCheckbox.onclick = function() {
                if (ignoreThisCheckbox.checked) {
                    ignoreAllCheckbox.checked = false;
                    // Update the user's cookie preferences
                    var popups = getPopupPreferences();
                    popups[warningName] = true;
                    setPopupPreferences(popups);
                }
            }
            ignoreAllCheckbox.onclick = function() {
                if (ignoreAllCheckbox.checked) {
                    ignoreThisCheckbox.checked = false;
                    // Update the user's cookie preferences
                    var popups = getPopupPreferences();
                    for (var key in popups) {
                        popups[key] = true;
                    }
                    setPopupPreferences(popups);
                }
            }
        } else {
            // If the user has not given consent, hide the checkboxes
            checkboxContainer.style.display = "none";
        }
    }

    // Show the modal
    modal.style.display = "block";
}

// Function to get the user's popup preferences from the cookie
function getPopupPreferences() {
  console.log("getPopupPreferences run");
  var cookie = document.cookie.split('; ').find(row => row.startsWith('popups='));
  if (cookie) {
      var cookieValue = cookie.split('=')[1];
      return JSON.parse(decodeURIComponent(cookieValue));
  } else {
      return {};
  }
}

// Function to set the user's popup preferences in the cookie
function setPopupPreferences(popups) {
  console.log("setPopupPreference run");
  document.cookie = "popups=" + encodeURIComponent(JSON.stringify(popups)) + "; path=/";
}

// Function to check the user's cookie preferences
function checkCookiePreferences(modalId, message, action, warningName) {
  // Check the user's cookies
    var consent = document.cookie.split('; ').find(row => row.startsWith('consent='));
    var popups = getPopupPreferences();

    // If the popups cookie doesn't exist and the user has given consent, create it
    if (consent && Object.keys(popups).length === 0) {
      console.log("Checks for popup existance, creates it");
      setPopupPreferences({[warningName]: false});
      popups = getPopupPreferences();
  }

    // If the user has not given consent, show the warning popup
    if (!consent) {
      console.log("Showing warning popup because user has not given consent");
      showWarningPopup(modalId, message, action, warningName);
    } else if (!popups[warningName]) {
      // If the user has given consent but has NOT opted to ignore this warning or all warnings, show the warning popup
      console.log("Showing warning popup because user has not opted to ignore this warning or all warnings");
      showWarningPopup(modalId, message, action, warningName);
  } else {
      // If the user has given consent and has opted to ignore this warning or all warnings, perform the action
      console.log("Performing action because user has given consent and has opted to ignore this warning or all warnings");
      action();
  }
}

// Attach the checkCookiePreferences function to the "Remove Post" button
var removePostButton = document.getElementById("removePostButton");
console.log(removePostButton);
if (removePostButton) {
    removePostButton.onclick = function(event) {
        console.log("Button clicked");
        event.preventDefault();  // Prevent the form from being submitted
        checkCookiePreferences(
            "warningModal",  // The ID of the modal to display
            "Warning: Removing a post will also delete any currently saved funds for that post. Consider using the transfer and delete form, or manually move funds from your Home page.",
            function() {
                // Action to perform if the user accepts the warning
                document.getElementById("removePostForm").submit();
            },
            "ignoreRemovePostWarning"  // The name of the warning
        );
    }
}

var commitSavingsButton = document.getElementById("commitSavingsButton");
if (commitSavingsButton) {
    commitSavingsButton.onclick = function(event) {
        event.preventDefault();  // Prevent the form from being submitted
        checkCookiePreferences(
            "warningModal",  // The ID of the modal to display
            "Warning: Committing changes will recalculate your current savings per post based on your account balance. This is only intended for newly created accounts, after a reset, or if you want to only reallocate funds accordingly.",
            function() {
                // Action to perform if the user accepts the warning
                document.getElementById("commitSavingsForm").submit();
            },
            "ignoreCommitSavingsWarning"  // The name of the warning
        );
    }
}

var resetPostsButton = document.getElementById("resetPostsButton");
if (resetPostsButton) {
    resetPostsButton.onclick = function(event) {
        event.preventDefault();  // Prevent the form from being submitted
        checkCookiePreferences(
            "warningModal",  // The ID of the modal to display
            "Warning: Resetting posts will not affect your transaction history or account balance. However it will delete all your posts. This action is not reversible.",
            function() {
                // Action to perform if the user accepts the warning
                document.getElementById("resetPostsForm").submit();
            },
            "ignoreResetPostsWarning"  // The name of the warning
        );
    }
}

var resetAccountButton = document.getElementById("resetAccountButton");
if (resetAccountButton) {
    resetAccountButton.onclick = function(event) {
        event.preventDefault();  // Prevent the form from being submitted
        checkCookiePreferences(
            "warningModal",  // The ID of the modal to display
            "Warning: Resetting your account will delete all of your posts, goals, allocation, savings, and account balance. This is meant as a clean reset. The data is not retrievable once deleted. But don't worry, this is not connected to your bank. It's just numbers on a page ;)",
            function() {
                // Action to perform if the user accepts the warning
                document.getElementById("resetAccountForm").submit();
            },
            "ignoreResetAccountWarning"  // The name of the warning
        );
    }
}

document.getElementById("deleteConfirmation").onclick = function() {
  var confirmation = window.confirm("Are you sure you want to delete your account and all your data? This action cannot be undone.");
  if (confirmation) {
    document.getElementById("deleteAccountForm").submit();
  }
};

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


// TABLE MODAL
// Get the modal
// Get the form element
var customSetupForm = document.getElementById("customSetupForm");

// Function to update the remaining percentage
function updateRemainingPercentage() {
  var initialRemainingAllocation = parseFloat(document.getElementById("initialRemainingAllocation").value);
  var inputs = document.getElementsByName("postAllocation[]");
  var totalAllocation = 0;
  for (var i = 0; i < inputs.length; i++) {
    totalAllocation += parseFloat(inputs[i].value) || 0;
  }
  var remainingPercentage = initialRemainingAllocation - totalAllocation;
  document.getElementById("remainingPercentage").innerText = "Remaining Percentage: " + remainingPercentage + "%";
  return remainingPercentage; // Return the remaining percentage
}

// Attach the updateRemainingPercentage function to the input change event
var inputs = document.getElementsByName("postAllocation[]");
for (var i = 0; i < inputs.length; i++) {
  inputs[i].addEventListener("input", updateRemainingPercentage);
}

// Update the remaining percentage when the page loads
updateRemainingPercentage();

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];
if (span) {
  span.onclick = function() {
    closeModal("customSetupModal");  // Close the modal
  }
}

var setupButton = document.getElementById("setupButton");
if (setupButton) {
  setupButton.onclick = function(event) {
    event.preventDefault();  // Prevent the form from being submitted
    customSetupModal.style.display = "block";  // Display the modal
  }
}

// Add functionality to add a new row
document.getElementById("addRowButton").onclick = function() {
  var table = document.getElementById("customSetupTable").getElementsByTagName('tbody')[0];
  var newRow = table.insertRow(table.rows.length);

  var cell1 = newRow.insertCell(0);
  var cell2 = newRow.insertCell(1);
  var cell3 = newRow.insertCell(2);

  cell1.innerHTML = '<input type="text" name="postName[]" placeholder="Name">';
  cell2.innerHTML = '<input type="number" name="postGoal[]" placeholder="Goal">';
  cell3.innerHTML = '<input type="number" name="postAllocation[]" placeholder="% Allocation">';

  // Attach the updateRemainingPercentage function to the input change event
  var inputs = document.getElementsByName("postAllocation[]");
  for (var i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener("input", updateRemainingPercentage);
  }
}

var suggestions = {
  "Financial:": ["Emergency Fund", "Retirement", "Pension", "Investment", "Debt Repayment", "Home Improvement", "Career Development", "Education"],
  "Recreational:": ["Personal Spending", "Technology", "Shopping", "Hobby", "Entertainment", "Dining Out", "Gaming", "Fun"],
  "Lifestyle & Goals:": ["Home Purchase", "Car Purchase", "Vacation/Travel", "Wedding", "Family", "Charity", "Home Decor", "Clothing"]
};

document.getElementById("showSuggestionsButton").onclick = function() {
  var container = document.getElementById("suggestionsContainer");
  var list = document.getElementById("suggestionsList");

  // Toggle the display of the container
  container.style.display = container.style.display === "none" ? "block" : "none";

  // Clear the existing list
  list.innerHTML = "";

  // Populate the list with suggestions
  for (var category in suggestions) {
    var categoryItem = document.createElement("li");
    categoryItem.textContent = category;
    var subList = document.createElement("ul");
    suggestions[category].forEach(function(suggestion) {
      var listItem = document.createElement("li");
      listItem.textContent = suggestion;
      subList.appendChild(listItem);
    });
    categoryItem.appendChild(subList);
    list.appendChild(categoryItem);
  }
};

customSetupForm.addEventListener("submit", function(event) {
  var remainingPercentage = updateRemainingPercentage();
  if (remainingPercentage < 0) {
    alert("Allocation exceeds 100%");
    event.preventDefault(); // Prevent the form from being submitted
  }
});

// Get the modal and button elements
var profileSettingsModal = document.getElementById("profileSettingsModal");
var profileSettingsButton = document.getElementById("profileSettingsButton");

// Open the modal when the button is clicked
profileSettingsButton.onclick = function() {
  profileSettingsModal.style.display = "block";
}

  

console.log("CookiePref Loaded");