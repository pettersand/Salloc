//// TABLE SORTING ////

function sortTable(n) {
    let table = document.getElementById("myTable");
    if (!table) return; // If the table doesn't exist, exit the function
    let switching = true;
    let dir = "desc"; // Set the sorting direction to descending
    let switchcount = 0;
  
    // Remove the sort symbol from all columns
    for (let i = 0; i < 5; i++) {
      table.rows[0].getElementsByTagName("TH")[i].innerHTML = table.rows[0].getElementsByTagName("TH")[i].innerHTML.replace(" ▲", "").replace(" ▼", "");
    }
  
    while (switching) {
      switching = false;
      const rows = table.rows;
      for (let i = 1; i < (rows.length - 1); i++) {
        let shouldSwitch = false;
        const x = rows[i].getElementsByTagName("TD")[n];
        const y = rows[i + 1].getElementsByTagName("TD")[n];
        let xVal, xMax, yVal, yMax;
  
        if (n === 3) { // if it's the progress bar column
          xVal = x.getElementsByTagName("progress")[0].value;
          xMax = x.getElementsByTagName("progress")[0].max;
          yVal = y.getElementsByTagName("progress")[0].value;
          yMax = y.getElementsByTagName("progress")[0].max;
        } else {
          xVal = Number(x.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''));
          yVal = Number(y.innerHTML.replace(/,/g, '').replace('%', '').replace('kr', ''));
        }
  
        if (dir === "desc" && ((n === 3 && (xVal / xMax) < (yVal / yMax)) || (isNaN(xVal) && x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) || (!isNaN(xVal) && xVal < yVal))) {
          shouldSwitch = true;
        } else if (dir === "asc" && ((n === 3 && (xVal / xMax) > (yVal / yMax)) || (isNaN(xVal) && x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) || (!isNaN(xVal) && xVal > yVal))) {
          shouldSwitch = true;
        }
  
        if (shouldSwitch) {
          rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
          switching = true;
          switchcount++;
        } else if (switchcount === 0 && dir === "desc") {
          dir = "asc";
          switching = true;
        }
      }
  
      // Add the sort symbol to the sorted column
      table.rows[0].getElementsByTagName("TH")[n].innerHTML += dir === "asc" ? " ▼" : " ▲";
    }
  }
  



// COOKIES HANDLING //

// Function to get the user's popup preferences from the cookie
function getPopupPreferences() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('popups='));
    if (cookie) {
      const cookieValue = cookie.split('=')[1];
      return JSON.parse(decodeURIComponent(cookieValue));
    }
    return {};
  }
  
  // Function to set the user's popup preferences in the cookie
  function setPopupPreferences(popups) {
    document.cookie = "popups=" + encodeURIComponent(JSON.stringify(popups)) + "; path=/";
  }
  
  // Function to check the user's cookie preferences
  function checkCookiePreferences(modalId, message, action, warningName) {
    const consent = document.cookie.split('; ').find(row => row.startsWith('consent='));
    let popups = getPopupPreferences();
  
    // If the popups cookie doesn't exist and the user has given consent, create it
    if (consent && Object.keys(popups).length === 0) {
      setPopupPreferences({ [warningName]: false });
      popups = getPopupPreferences();
    }
  
    // Determine whether to show the warning popup or perform the action
    if (!consent || !popups[warningName]) {
      showWarningPopup(modalId, message, action, warningName);
    } else {
      action();
    }
  }

// MODAL HANDLING //

// Function to open a modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'block';
    } else {
      console.error(`Modal with ID ${modalId} not found.`);
    }
  }
  
  // Function to close a modal
  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'none';
    } else {
      console.error(`Modal with ID ${modalId} not found.`);
    }
  }
  
// Function to close a modal when clicking outside of it, with an option to disable this behavior
function setupModalClickOutsideClose(modalId, enableClickOutsideClose = true) {
    const modal = document.getElementById(modalId);
    if (modal) {
      if (enableClickOutsideClose) {
        window.onclick = function(event) {
          if (event.target === modal) {
            modal.style.display = 'none';
          }
        };
      }
    } else {
      console.error(`Modal with ID ${modalId} not found.`);
    }
  }


  // WARNING POPUP FUNCTIONALITY //

  function showWarningPopup(modalId, message, action, warningName) {
    const modal = document.getElementById(modalId);
    if (!modal) return; // If there's no modal on the page, stop the script
  
    // Set the warning message
    const warningMessageElement = document.getElementById("warningMessage");
    if (warningMessageElement) {
      warningMessageElement.textContent = message;
    }
  
    // Handle the "Cancel" and "Accept" buttons
    const cancelButton = document.getElementById("cancelButton");
    const acceptButton = document.getElementById("acceptButton");
    if (cancelButton) cancelButton.onclick = () => modal.style.display = "none";
    if (acceptButton) acceptButton.onclick = () => { modal.style.display = "none"; action(); };
  
    // Check the user's cookies
    const consent = document.cookie.split('; ').find(row => row.startsWith('consent='));
  
    // Get the checkbox container
    const checkboxContainer = document.getElementById("checkboxContainer");
    const ignoreThisCheckbox = document.getElementById("ignoreThisCheckbox");
    const ignoreAllCheckbox = document.getElementById("ignoreAllCheckbox");
  
    // Handle the checkboxes
    if (ignoreThisCheckbox && ignoreAllCheckbox && checkboxContainer) {
      if (consent) {
        checkboxContainer.style.display = "block";
        ignoreThisCheckbox.onclick = handleCheckboxClick(warningName, true);
        ignoreAllCheckbox.onclick = handleCheckboxClick(warningName, false);
      } else {
        checkboxContainer.style.display = "none";
      }
    }
  
    // Show the modal
    modal.style.display = "block";
  }
  
  function handleCheckboxClick(warningName, isIgnoreThis) {
    return function() {
      const popups = getPopupPreferences();
      if (isIgnoreThis) {
        popups[warningName] = true;
      } else {
        for (const key in popups) {
          popups[key] = true;
        }
      }
      setPopupPreferences(popups);
    };
  }

  function addButtonClickHandler(buttonId, modalId, warningMessage, formId, warningName) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.onclick = function(event) {
            event.preventDefault(); // Prevent the form from being submitted
            checkCookiePreferences(
                modalId, // The ID of the modal to display
                warningMessage,
                function() {
                    // Action to perform if the user accepts the warning
                    document.getElementById(formId).submit();
                },
                warningName // The name of the warning
            );
        };
    }
}

addButtonClickHandler(
    "removePostButton",
    "warningModal",
    "Warning: Removing a post will also delete any currently saved funds for that post. Consider using the transfer and delete form, or manually move funds from your Home page.",
    "removePostForm",
    "ignoreRemovePostWarning"
);

addButtonClickHandler(
    "commitSavingsButton",
    "warningModal",
    "Warning: Committing changes will recalculate your current savings per post based on your account balance. This is only intended for newly created accounts, after a reset, or if you want to only reallocate funds accordingly.",
    "commitSavingsForm",
    "ignoreCommitSavingsWarning"
);

addButtonClickHandler(
    "resetPostsButton",
    "warningModal",
    "Warning: Resetting posts will not affect your transaction history or account balance. However it will delete all your posts. This action is not reversible.",
    "resetPostsForm",
    "ignoreResetPostsWarning"
);

addButtonClickHandler(
    "resetAccountButton",
    "warningModal",
    "Warning: Resetting your account will delete all of your posts, goals, allocation, savings, and account balance. This is meant as a clean reset. The data is not retrievable once deleted. But don't worry, this is not connected to your bank. It's just numbers on a page ;)",
    "resetAccountForm",
    "ignoreResetAccountWarning"
);

if (document.getElementById("deleteConfirmation")) {
  function showDeleteConfirmation(modalId, message, action) {
      // Show the warning popup without checking cookie preferences
      showWarningPopup(modalId, message, action);
    }

  document.getElementById("deleteConfirmation").onclick = function(event) {
    event.preventDefault(); // Prevent the form from being submitted immediately
    showDeleteConfirmation(
      "warningModal", // The ID of the modal to display
      "Are you sure you want to delete your account and all your data? This action cannot be undone.",
      function() {
        // Action to perform if the user accepts the warning
        document.getElementById("deleteAccountForm").submit();
      }
    );
  };
}

//// REGISTRATION MODAL ///////

// Get the modal
if (document.getElementById("myModal")) {
  const modal = document.getElementById("myModal");
  if (modal) {
    // Get the <span> element that closes the modal
    const span = document.getElementsByClassName("close")[0];
    if (span) {
      span.onclick = function() {
        closeModal("myModal"); // Close the modal
      };
    }

    const registerButton = document.getElementById("registerButton");
    if (registerButton) {
      registerButton.onclick = function(event) {
        event.preventDefault(); // Prevent the form from being submitted
        openModal("myModal"); // Display the modal
      };
    }

    // Handle consent checkboxes
    const consentCheckbox = document.getElementById("consent");
    const noConsentCheckbox = document.getElementById("noConsent");
    const consentField = document.getElementById("consentField");

    if (consentCheckbox && noConsentCheckbox) {
      consentCheckbox.onclick = handleCheckboxClick("consent", false);
      noConsentCheckbox.onclick = handleCheckboxClick("noConsent", false);
    }

    const continueButton = document.getElementById("continueButton");
    if (continueButton && consentField) {
      continueButton.onclick = function() {
        if (consentCheckbox.checked) {
          consentField.value = 'yes';
        } else if (noConsentCheckbox.checked) {
          consentField.value = 'no';
        }
        // Submit the form
        const form = document.getElementById("registerForm");
        if (form) {
          form.submit();
        }
      };
    }
  }
}


//// CUSTOM SETUP TABLE FORM ////

const customSetupForm = document.getElementById("customSetupForm");

// Function to update the remaining percentage
if (document.getElementById("customSetupForm")) {
  function updateRemainingPercentage() {
    const initialRemainingAllocation = parseFloat(document.getElementById("initialRemainingAllocation").value);
    const inputs = document.getElementsByName("postAllocation[]");
    let totalAllocation = 0;
    for (let i = 0; i < inputs.length; i++) {
      totalAllocation += parseFloat(inputs[i].value) || 0;
    }
    const remainingPercentage = initialRemainingAllocation - totalAllocation;
    document.getElementById("remainingPercentage").innerText = "Remaining Percentage: " + remainingPercentage + "%";
    return remainingPercentage; // Return the remaining percentage
  }

  // Attach the updateRemainingPercentage function to the input change event
  const inputs = document.getElementsByName("postAllocation[]");
  for (let i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener("input", updateRemainingPercentage);
  }

  // Update the remaining percentage when the page loads
  updateRemainingPercentage();

  // Get the <span> element that closes the modal
  const span = document.getElementsByClassName("close")[0];
  if (span) {
    span.onclick = function() {
      closeModal("customSetupModal"); // Close the modal
    };
  }

  const setupButton = document.getElementById("setupButton");
  if (setupButton) {
    setupButton.onclick = function(event) {
      event.preventDefault(); // Prevent the form from being submitted
      openModal("customSetupModal"); // Display the modal
    };
  }

  // Add functionality to add a new row
  document.getElementById("addRowButton").onclick = function() {
    const table = document.getElementById("customSetupTable").getElementsByTagName('tbody')[0];
    const newRow = table.insertRow(table.rows.length);

    const cell1 = newRow.insertCell(0);
    const cell2 = newRow.insertCell(1);
    const cell3 = newRow.insertCell(2);

    cell1.innerHTML = '<input type="text" name="postName[]" placeholder="Name">';
    cell2.innerHTML = '<input type="number" name="postGoal[]" placeholder="Goal">';
    cell3.innerHTML = '<input type="number" name="postAllocation[]" placeholder="% Allocation">';

    // Attach the updateRemainingPercentage function to the input change event
    const inputs = document.getElementsByName("postAllocation[]");
    for (let i = 0; i < inputs.length; i++) {
      inputs[i].addEventListener("input", updateRemainingPercentage);
    }
  }

  const suggestions = {
    "Financial:": ["Emergency Fund", "Retirement", "Pension", "Investment", "Debt Repayment", "Home Improvement", "Career Development", "Education"],
    "Recreational:": ["Personal Spending", "Technology", "Shopping", "Hobby", "Entertainment", "Dining Out", "Gaming", "Fun"],
    "Lifestyle & Goals:": ["Home Purchase", "Car Purchase", "Vacation/Travel", "Wedding", "Family", "Charity", "Home Decor", "Clothing"]
  };

  document.getElementById("showSuggestionsButton").onclick = function() {
    const container = document.getElementById("suggestionsContainer");
    const list = document.getElementById("suggestionsList");

    // Toggle the display of the container
    container.style.display = container.style.display === "none" ? "block" : "none";

    // Clear the existing list
    list.innerHTML = "";

    // Populate the list with suggestions
    for (const category in suggestions) {
      const categoryItem = document.createElement("li");
      categoryItem.textContent = category;
      const subList = document.createElement("ul");
      suggestions[category].forEach(function(suggestion) {
        const listItem = document.createElement("li");
        listItem.textContent = suggestion;
        subList.appendChild(listItem);
      });
      categoryItem.appendChild(subList);
      list.appendChild(categoryItem);
    }
  };

  customSetupForm.addEventListener("submit", function(event) {
    const remainingPercentage = updateRemainingPercentage();
    if (remainingPercentage < 0) {
      alert("Allocation exceeds 100%");
      event.preventDefault(); // Prevent the form from being submitted
    }
  });
}

//// PROFILE SETTING MODAL ////

const profileSettingsButton = document.getElementById("profileSettingsButton");
if (profileSettingsButton) {
  profileSettingsButton.onclick = function() {
    openModal("profileSettingsModal");
  };
}