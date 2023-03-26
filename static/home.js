const dropdown = document.getElementById("dropdown");
const admClasses = document.getElementById("admClasses");
const classrooms = document.getElementById("classrooms");
const commexmhall = document.getElementById("commexmhall");
const commonexmhall = document.getElementById("commonexmhall");
const drawhall = document.getElementById("drawhall");
const semhall = document.getElementById("semhall");

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
