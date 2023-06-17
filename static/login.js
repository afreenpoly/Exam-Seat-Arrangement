// Select the username input field
const usernameInput = document.getElementById("username-field");

// Define the pattern for the username
const usernamePattern = /^JEC\w{3}$/;

// Add an event listener to the username input field to check the pattern on input
usernameInput.addEventListener("input", () => {
  // Get the value of the username input field
  const username = usernameInput.value;

  // Check if the username matches the pattern
  if (usernamePattern.test(username)) {
    // The username matches the pattern, remove any previous error messages
    usernameInput.setCustomValidity("");
  } else {
    // The username doesn't match the pattern, set a custom error message
    usernameInput.setCustomValidity(
      "Username must start with 'JEC' and be followed by 3 numeric characters"
    );
  }
});

// Select the password input field
const passwordInput = document.getElementById("password-field");

// Add an event listener to the password input field to check the strength on input
passwordInput.addEventListener("input", () => {
  // Get the value of the password input field
  const password = passwordInput.value;

  // Define the regular expressions for different password strength criteria
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSymbols = /[^\w\s]/.test(password);

  // Define the minimum number of criteria required for a strong password
  const minCriteria = 3;

  // Check the password strength and set a custom error message if necessary
  if (
    password.length >= 8 &&
    [hasUpperCase, hasLowerCase, hasNumbers, hasSymbols].filter((c) => c).length >= minCriteria
  ) {
    // The password meets the strength criteria, remove any previous error messages
    passwordInput.setCustomValidity("");
  } else {
    // The password doesn't meet the strength criteria, set a custom error message
    passwordInput.setCustomValidity(
      "Password must be at least 8 characters long and contain at least 3 of the following: uppercase letters, lowercase letters, numbers, symbols"
    );
  }
});

// // Select the password input field and create a new button element
// const toggleButton = document.createElement("button");

// // Set the text and type of the toggle button
// toggleButton.innerText = "Show";
// toggleButton.type = "button";

// // Add a click event listener to toggle the password visibility
// toggleButton.addEventListener("click", () => {
//   if (passwordInput.type === "password") {
//     passwordInput.type = "text";
//     toggleButton.innerText = "Hide";
//   } else {
//     passwordInput.type = "password";
//     toggleButton.innerText = "Show";
//   }
// });

// // Add the toggle button to the DOM
// passwordInput.parentNode.appendChild(toggleButton);


