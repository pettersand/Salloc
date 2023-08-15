/// NEW SORTING FUNCTION MAIN PAGE ////
// Function to sort rows based on a selected column


// COOKIES HANDLING //

// Function to get the user's popup preferences from the cookie
function getPopupPreferences() {
  const cookie = document.cookie
    .split("; ")
    .find((row) => row.startsWith("popups="));
  if (cookie) {
    const cookieValue = cookie.split("=")[1];
    return JSON.parse(decodeURIComponent(cookieValue));
  }
  return {};
}

// Function to set the user's popup preferences in the cookie
function setPopupPreferences(popups) {
  document.cookie =
    "popups=" + encodeURIComponent(JSON.stringify(popups)) + "; path=/";
}

// Function to check the user's cookie preferences
function checkCookiePreferences(modalId, message, action, warningName) {
  const consent = document.cookie
    .split("; ")
    .find((row) => row.startsWith("consent="));
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
    modal.style.display = "block";
  }
}

// JavaScript to close all modals with the class "modal"
const modals = document.querySelectorAll(".modal");
modals.forEach(function (modal) {
  const modalId = modal.id;
  const closeButton = modal.querySelector(".close");
  if (closeButton) {
    closeButton.onclick = function () {
      closeModal(modalId);
    };
  }
});

// Function to close the modal
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "none";
  }
}

// Function to handle the "Esc" key press
function handleEscKey(event) {
  if (event.key === "Escape") {
    modals.forEach(function (modal) {
      closeModal(modal.id);
    });
  }
}

// Function to handle clicking outside the modal
function handleClickOutside(event) {
  modals.forEach(function (modal) {
    if (event.target === modal) {
      closeModal(modal.id);
    }
  });
}

// Attach event listeners for the "Esc" key and clicking outside the modal
document.addEventListener("keydown", handleEscKey);
document.addEventListener("click", handleClickOutside);

// Attach click event to the close button of each modal
modals.forEach(function (modal) {
  const modalId = modal.id;
  const closeButton = modal.querySelector(".close");
  if (closeButton) {
    closeButton.onclick = function () {
      closeModal(modalId);
    };
  }
});

// CHECKBOX HANDLING //

function setupSingleCheckbox(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return; // If the container doesn't exist, stop the script

  const checkboxes = container.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.onclick = () => {
      checkboxes.forEach((cb) => {
        if (cb !== checkbox) {
          cb.checked = false;
        }
      });
    };
  });
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
  if (cancelButton) cancelButton.onclick = () => (modal.style.display = "none");
  if (acceptButton)
    acceptButton.onclick = () => {
      modal.style.display = "none";
      action();
    };

  // Check the user's cookies
  const consent = document.cookie
    .split("; ")
    .find((row) => row.startsWith("consent="));

  // Get the checkbox container
  const checkboxContainer = document.getElementById("checkboxContainer");
  const ignoreThisCheckbox = document.getElementById("ignoreThisCheckbox");
  const ignoreAllCheckbox = document.getElementById("ignoreAllCheckbox");

  // Handle the checkboxes
  if (ignoreThisCheckbox && ignoreAllCheckbox && checkboxContainer) {
    if (consent) {
      checkboxContainer.style.display = "block";
      setupSingleCheckbox("checkboxContainer");
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
  return function () {
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

function addButtonClickHandler(
  buttonId,
  modalId,
  warningMessage,
  formId,
  warningName
) {
  const button = document.getElementById(buttonId);
  if (button) {
    button.onclick = function (event) {
      event.preventDefault(); // Prevent the form from being submitted
      checkCookiePreferences(
        modalId, // The ID of the modal to display
        warningMessage,
        function () {
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

addButtonClickHandler(
  "resetSavingsButton",
  "warningModal",
  "Warning: Resetting your savings will delete all your currently allocated saved funds. Meaning you will have to reallocate again with the commit button.",
  "resetSavingsForm",
  "ignoreResetSavingsWarning"
);

addButtonClickHandler(
  "setSavingsButton",
  "warningModal",
  "Warning: Setting your total savings will override your current balance. If there is a significant difference this can adversely affect your data.",
  "setSavingsForm",
  "ignoreSetSavingsWarning"
);

if (document.getElementById("deleteConfirmation")) {
  function showDeleteConfirmation(modalId, message, action) {
    // Show the warning popup without checking cookie preferences
    showWarningPopup(modalId, message, action);
  }

  document.getElementById("deleteConfirmation").onclick = function (event) {
    event.preventDefault(); // Prevent the form from being submitted immediately
    showDeleteConfirmation(
      "warningModal", // The ID of the modal to display
      "Are you sure you want to delete your account and all your data? This action cannot be undone.",
      function () {
        // Action to perform if the user accepts the warning
        document.getElementById("deleteAccountForm").submit();
      }
    );
  };
}

// Get the privacy link element
const privacyLink = document.getElementById("privacyLink");

// Add a click event listener to the privacy link
if (privacyLink) {
  privacyLink.onclick = function (event) {
    event.preventDefault(); // Prevent the default link behavior
    openModal("privacyModal"); // Open the privacy modal
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
      span.onclick = function () {
        closeModal("myModal"); // Close the modal
      };
    }

    const registerButton = document.getElementById("registerButton");
    if (registerButton) {
      registerButton.onclick = function (event) {
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

      // Call the function to set up the only one checkbox functionality
      setupSingleCheckbox("checkboxContainer");
    }

    const continueButton = document.getElementById("continueButton");
    if (continueButton && consentField) {
      continueButton.onclick = function () {
        if (consentCheckbox.checked) {
          consentField.value = "yes";
        } else if (noConsentCheckbox.checked) {
          consentField.value = "no";
        }
        // Submit the form
        const form = document.getElementById("registerForm");
        if (form) {
          form.submit();
        }
      };
    }

    const exitButton = document.getElementById("exitButton");
    if (exitButton) {
      exitButton.onclick = function () {
        closeModal("myModal"); // Close the modal
      };
    }
  }
}

//// CUSTOM SETUP TABLE FORM ////
if (document.getElementById("customSetupForm")) {
  const customSetupForm = document.getElementById("customSetupForm");
  const customSetupModal = document.getElementById("customSetupModal");
  // Function to update the remaining percentage
  function updateRemainingPercentage() {
    const initialRemainingAllocation = parseFloat(
      document.getElementById("initialRemainingAllocation").value
    );
    const inputs = document.getElementsByName("postAllocation[]");
    let totalAllocation = 0;
    for (let i = 0; i < inputs.length; i++) {
      totalAllocation += parseFloat(inputs[i].value) || 0;
    }
    const remainingPercentage = initialRemainingAllocation - totalAllocation;
    document.getElementById("remainingPercentage").innerText =
      "Remaining Percentage: " + remainingPercentage + "%";
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
  const span = customSetupModal.querySelector(".close"); // Use querySelector on the modal element
  if (span) {
    span.onclick = function () {
      closeModal("customSetupModal"); // Close the modal
    };
  }

  const setupButton = document.getElementById("setupButton");
  if (setupButton) {
    setupButton.onclick = function (event) {
      event.preventDefault(); // Prevent the form from being submitted
      openModal("customSetupModal"); // Display the modal
    };
  }

  // Add functionality to add a new row
  document.getElementById("addRowButton").onclick = function () {
    const table = document
      .getElementById("customSetupTable")
      .getElementsByTagName("tbody")[0];
    const newRow = table.insertRow(table.rows.length);

    const cell1 = newRow.insertCell(0);
    const cell2 = newRow.insertCell(1);
    const cell3 = newRow.insertCell(2);

    cell1.innerHTML =
      '<input type="text" name="postName[]" placeholder="Name">';
    cell2.innerHTML =
      '<input type="number" name="postGoal[]" placeholder="Goal">';
    cell3.innerHTML =
      '<input type="number" name="postAllocation[]" placeholder="% Allocation">';

    // Attach the updateRemainingPercentage function to the input change event
    const inputs = document.getElementsByName("postAllocation[]");
    for (let i = 0; i < inputs.length; i++) {
      inputs[i].addEventListener("input", updateRemainingPercentage);
    }
  };

  const suggestions = {
    "Financial:": [
      "Emergency Fund",
      "Retirement",
      "Pension",
      "Investment",
      "Debt Repayment",
      "Home Improvement",
      "Career Development",
      "Education",
    ],
    "Recreational:": [
      "Personal Spending",
      "Technology",
      "Shopping",
      "Hobby",
      "Entertainment",
      "Dining Out",
      "Gaming",
      "Fun",
    ],
    "Lifestyle & Goals:": [
      "Home Purchase",
      "Car Purchase",
      "Vacation/Travel",
      "Wedding",
      "Family",
      "Charity",
      "Home Decor",
      "Clothing",
    ],
  };

  document.getElementById("showSuggestionsButton").onclick = function () {
    const container = document.getElementById("suggestionsContainer");
    const list = document.getElementById("suggestionsList");

    // Toggle the display of the container
    container.style.display =
      container.style.display === "none" ? "block" : "none";

    // Clear the existing list
    list.innerHTML = "";

    // Populate the list with suggestions
    for (const category in suggestions) {
      const categoryItem = document.createElement("li");
      categoryItem.textContent = category;
      const subList = document.createElement("ul");
      suggestions[category].forEach(function (suggestion) {
        const listItem = document.createElement("li");
        listItem.textContent = suggestion;
        subList.appendChild(listItem);
      });
      categoryItem.appendChild(subList);
      list.appendChild(categoryItem);
    }
  };

  customSetupForm.addEventListener("submit", function (event) {
    const remainingPercentage = updateRemainingPercentage();
    if (remainingPercentage < 0) {
      alert("Allocation exceeds 100%");
      event.preventDefault(); // Prevent the form from being submitted
    }
  });
}

//// PROFILE SETTING MODAL ////
if (document.getElementById("profileSettingsButton")) {
  const profileSettingsButton = document.getElementById(
    "profileSettingsButton"
  );
  if (profileSettingsButton) {
    profileSettingsButton.onclick = function () {
      openModal("profileSettingsModal");

      const consentCookies = document.getElementById("consentCookies");
      const noCookies = document.getElementById("noCookies");
      const consentUpdate = document.getElementById("consentUpdate");

      setupSingleCheckbox("profileSettingsForm");

      const continueButton = document.getElementById("updateConsent");
      if (continueButton && consentUpdate) {
        continueButton.onclick = function () {
          if (consentCookies.checked) {
            consentUpdate.value = "yes";
          } else if (noCookies.checked) {
            consentUpdate.value = "no";
          }
          // The form will submit normally with the updated consent value
        };
      }
    };
  }
}

//// UPDATING USER EDITS FROM TABLE ////
$(document).ready(function () {
  const initialRemainingAllocation = parseInt($("#hiddenRemainAlloc").val());
  let totalAllocation = initialRemainingAllocation;

  function updateRemainingAllocation() {
      let currentTotalAllocation = 0;
      $(".flex-salloc-input").each(function () {
          let salloc = $(this).val().trim();
          if (salloc === "" || isNaN(salloc)) {
              salloc = "0";
          }
          const parsedSalloc = parseInt(salloc);
          currentTotalAllocation += parsedSalloc;
      });
      totalAllocation = 100 - currentTotalAllocation;
      $("#remainingAllocationCounter").text(totalAllocation);

      if (totalAllocation < 0 || totalAllocation > 100) {
          $("#updateButton").prop("disabled", true);
          $("#updateButton").text("Exceeds 100%");
      } else {
          $("#updateButton").prop("disabled", false);
          $("#updateButton").text("Update Changes");
      }
  }

  $(".div-table").on("input", ".flex-salloc-input", function () {
      $(this).addClass("edited");
      updateRemainingAllocation();
  });

  const editableDivs = document.querySelectorAll("[contenteditable=true]");
  editableDivs.forEach(function (div) {
      $(div).on("keyup", function () {
          console.log("Editable div input detected");
          $(this).addClass("edited");
      });
  });

  $("#updateButton").click(function (event) {
      const editedData = [];
      $(".flex-row").each(function () {
          const row = $(this);
          const postName = row.find(".flex-post").text().trim();
          const oldName = row.find(".flex-post").data("old-name");
          const goal = parseInt(row.find(".flex-goal span").text().replace(/,/g, "").replace(" kr", ""));
          const salloc = parseInt(row.find(".flex-salloc-input").val());

          if (row.find(".edited").length > 0) {
              editedData.push({
                  postName: postName,
                  oldName: oldName,
                  goal: goal,
                  salloc: salloc,
              });
          }
      });

      console.log(JSON.stringify(editedData));
      $.ajax({
          url: "/salloc/update_table",
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify(editedData),
          success: function (response) {
              location.reload();
          },
          error: function (jqXHR, textStatus, errorThrown) {
              alert("An error occurred: " + textStatus);
          }
      });
  });
});






$(document).ready(function () {
  // Open the contact modal when the link in the footer is clicked
  $("#contactLink").click(function () {
    $("#contactModal").show();
  });

  // Close the contact modal when the close button is clicked
  $("#contactModal .close").click(function () {
    $("#contactModal").hide();
  });
});

$(document).ready(function () {
  // Open the contact modal when the link in the header or footer is clicked
  $(".contactLink").click(function (event) {
    event.preventDefault(); // Prevent the default link behavior
    $("#contactModal").show();
  });

  // Close the contact modal when the close button is clicked
  $("#contactModal .close").click(function () {
    $("#contactModal").hide();
  });
});


$(document).ready(function () {
  $("#setupGuideLink").click(function (event) {
    event.preventDefault(); // Prevent the default behavior of the anchor tag
    openModal("setupGuideModal");
  });
});


//// INFO MODAL POPUP ////
function showInfo(event) {
  // Determine the infoType based on the parent container's class or ID
  const parentContainer = event.target.closest(".item");
  let infoType = "";
  if (parentContainer.querySelector("#setSavings")) infoType = "setSavings";
  if (parentContainer.querySelector("#removePostButton"))
    infoType = "removePost";
  if (parentContainer.querySelector("#setupButton")) infoType = "setupCustom";
  if (parentContainer.querySelector("#generateTemplateButton"))
    infoType = "generateTemplate";
  if (parentContainer.querySelector("#commitSavingsButton"))
    infoType = "commitSavings";
  if (parentContainer.querySelector("#allocateButton"))
    infoType = "allocateUndefined";
  if (parentContainer.querySelector("#depositButton"))
    infoType = "depositFunds";
  if (parentContainer.querySelector("#specificDepositButton"))
    infoType = "specificDeposit";
  if (parentContainer.querySelector("#withdrawButton"))
    infoType = "withdrawFunds";
  if (parentContainer.querySelector("#moveFundsButton")) 
    infoType = "moveFunds";
  if (parentContainer.querySelector("#transferFundsButton"))
    infoType = "transferFunds";
  // Add more conditions as needed

  const infoContent = {
    setSavings: "Info: Sets the total balance of your account.",
    removePost:
      "Info: Removes a post and all its values completely, without transfer.",
    setupCustom: "Info: Add posts and their goal / allocation values.",
    generateTemplate:
      "Info: Generates a template post setup. Great learning tool.",
    commitSavings:
      "Info: Commits current balance to your post based on % Allocation spread.",
    allocateUndefined:
      "Info: Adds any excess funds to a spread based on your % Allocation or to a specified post.",
    depositFunds: "Info: Deposits funds evenly spread based on % Allocation.",
    specificDeposit: "Info: Deposits funds directly to specified post only.",
    withdrawFunds: "Info: Withdraws amount from specified post.",
    moveFunds: "Info: Moves specified amount from one post to another.",
    transferFunds:
      "Info: Moves all funds from one post to your destination, then deletes the post entirely.",

    // Add more content as needed
  };

  // Remove any existing tooltip
  const existingTooltip = document.querySelector(".tooltip");
  if (existingTooltip) existingTooltip.remove();

  // Create a new tooltip element
  const tooltip = document.createElement("div");
  tooltip.className = "tooltip";
  tooltip.innerText = infoContent[infoType];

  // Append the tooltip to the document (temporarily, to get its dimensions)
  document.body.appendChild(tooltip);

  // Position the tooltip to the left of the clicked element
  const iconElement = event.target.closest(".info-icon");
  const iconRect = iconElement.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();
  tooltip.style.left = iconRect.left - tooltipRect.width - 250 + "px"; // 10px gap to the left
  tooltip.style.top = iconRect.top - 50 + "px";

  // Show the tooltip
  tooltip.style.display = "block";
}

// Optional: Hide the tooltip when clicking anywhere else on the page
document.addEventListener("click", function (event) {
  if (!event.target.closest(".info-icon")) {
    const tooltip = document.querySelector(".tooltip");
    if (tooltip) tooltip.style.display = "none";
  }
});

//// NOTIFICATIONS / CONFIRMATIONS ////
document.addEventListener("DOMContentLoaded", function() {
  const flashes = document.querySelector(".flashes");
  if (flashes && flashes.children.length > 0) {
    flashes.style.display = "block";
  }
});
// This code will hide the flash message after 5 seconds
setTimeout(function() {
  document.querySelector('.flashes').style.display = 'none';
}, 4000);

function showError(message) {
  const errorModal = document.getElementById("errorModal");
  const errorMessage = document.getElementById("errorMessage");
  errorMessage.textContent = message;
  errorModal.style.display = "block";

  // Close button functionality
  const closeButton = errorModal.querySelector(".close");
  if (closeButton) {
    closeButton.onclick = function () {
      errorModal.style.display = "none";
    };
  }
}

//// TABLE SORTER ////
$(document).ready(function () {
  function sortRows(columnIndex, ascending) {
    const rows = $(".flex-row").not(":first").get(); // Exclude the header row
    rows.sort(function (a, b) {
      let aValue, bValue;
    
      if (columnIndex === 0) { // Post Name
        aValue = $(a).find(".flex-post").text().trim();
        bValue = $(b).find(".flex-post").text().trim();
        return ascending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      } else if (columnIndex === 1 || columnIndex === 2) { // Saved or Goal
        aValue = parseFloat($(a).find(columnIndex === 1 ? ".flex-saved" : ".flex-goal span").text().replace(/[^\d.]/g, ""));
        bValue = parseFloat($(b).find(columnIndex === 1 ? ".flex-saved" : ".flex-goal span").text().replace(/[^\d.]/g, ""));
      } else if (columnIndex === 3) { // Progress
        const progressA = $(a).find("progress");
        const progressB = $(b).find("progress");
        aValue = (parseFloat(progressA.attr("value")) / parseFloat(progressA.attr("max"))) * 100;
        bValue = (parseFloat(progressB.attr("value")) / parseFloat(progressB.attr("max"))) * 100;
      } else if (columnIndex === 4) { // Salloc
        aValue = parseFloat($(a).find(".flex-salloc-input").val());
        bValue = parseFloat($(b).find(".flex-salloc-input").val());
      }
    
      return ascending ? aValue - bValue : bValue - aValue;
    });

    $(".div-table .flex-row").not(":first").remove(); // Remove existing rows
    $(".div-table").append(rows); // Re-append the sorted rows
  }

  function handleHeaderClick(event) {
    const $header = $(event.currentTarget);
    const columnIndex = $header.index();
    const ascending = $header.data("ascending") || false; // Get current sort direction
    sortRows(columnIndex, ascending); // Sort rows
    $header.data("ascending", !ascending); // Toggle sort direction
    // Update arrows
    $(".sort-arrow").remove(); // Remove existing arrows
    const arrow = ascending ? "↑" : "↓"; // Set arrow based on sort direction
    $header.append(`<span class="sort-arrow">${arrow}</span>`); // Add arrow to header
  }

  // Add click event listener to sortable headers
  $(".sortable").on("click", handleHeaderClick);

  // Default sort by progress bar (replace 3 with the correct index of the progress column)
  sortRows(3, false);

  // Add an arrow to the default sorted column
  $(".flex-progress-h").append('<span class="sort-arrow">↓</span>'); // Add arrow to progress header
});


function setCurrency(currencyType) {
  // You can use AJAX here to send the selected currency to the server
  // Example using jQuery:
  $.post("/salloc/set_currency", { currency_type: currencyType }, function() {
      location.reload(); // Reload the page to apply the new currency setting
  });
}