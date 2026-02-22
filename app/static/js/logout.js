// Global functions for logout logic
function confirmLogout(event) {
  event.preventDefault();
  document.getElementById("logout_modal").showModal();
}

function performLogout() {
  localStorage.setItem("show_logout_toast", "true");
  window.location.href = "/logout";
}

document.addEventListener("DOMContentLoaded", () => {
  // Check for logout toast flag
  if (localStorage.getItem("show_logout_toast") === "true") {
    const toast = document.getElementById("logout_toast");
    if (toast) {
      toast.classList.remove("hidden");
      setTimeout(() => {
        toast.classList.add("hidden");
      }, 3000);
    }
    localStorage.removeItem("show_logout_toast");
  }
});