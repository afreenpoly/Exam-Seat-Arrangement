const dropdownContainer = document.getElementById("dropdowns-container");
const dropdown = document.getElementById("dropdown");
const admClasses = document.getElementById("admClasses");
const classrooms = document.getElementById("classrooms");
const commexmhall = document.getElementById("commexmhall");
const commonexmhall = document.getElementById("commonexmhall");
const drawhall = document.getElementById("drawhall");
const semhall = document.getElementById("semhall");

// Add event listener to initial dropdown
dropdown.addEventListener("change", function () {
  admClasses.classList.add("hidden");
  classrooms.classList.add("hidden");
  commexmhall.classList.add("hidden");
  commonexmhall.classList.add("hidden");
  drawhall.classList.add("hidden");
  semhall.classList.add("hidden");

  if (dropdown.value === "1") {
    admClasses.classList.remove("hidden");
  } else if (dropdown.value === "2") {
    classrooms.classList.remove("hidden");
  } else if (dropdown.value === "3") {
    commexmhall.classList.remove("hidden");
  } else if (dropdown.value === "4") {
    commonexmhall.classList.remove("hidden");
  } else if (dropdown.value === "5") {
    drawhall.classList.remove("hidden");
  } else if (dropdown.value === "6") {
    semhall.classList.remove("hidden");
  }
});

// Add event listeners to dynamically generated dropdowns
document.getElementById("noofclass").addEventListener("change", function() {
  const numDropdowns = parseInt(this.value);
  dropdownContainer.innerHTML = "";

  for (let i = 0; i < numDropdowns; i++) {
    const dropdown = document.createElement("select");
    dropdown.name = `dropdown-${i}`;
    dropdown.innerHTML = document.getElementById("dropdown").innerHTML;
    dropdownContainer.appendChild(dropdown);

    dropdown.addEventListener("change", function () {
      admClasses.classList.add("hidden");
      classrooms.classList.add("hidden");
      commexmhall.classList.add("hidden");
      commonexmhall.classList.add("hidden");
      drawhall.classList.add("hidden");
      semhall.classList.add("hidden");

      if (dropdown.value === "1") {
        admClasses.classList.remove("hidden");
      } else if (dropdown.value === "2") {
        classrooms.classList.remove("hidden");
      } else if (dropdown.value === "3") {
        commexmhall.classList.remove("hidden");
      } else if (dropdown.value === "4") {
        commonexmhall.classList.remove("hidden");
      } else if (dropdown.value === "5") {
        drawhall.classList.remove("hidden");
      } else if (dropdown.value === "6") {
        semhall.classList.remove("hidden");
      }
    });
  }
});
