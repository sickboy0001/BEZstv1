// Global functions for logout logic
const toastElement = document.getElementById('logout_toast');
if (toastElement) {
  const toast = new bootstrap.Toast(toastElement);
  toast.show();
}
function performLogout() {
  localStorage.setItem("show_logout_toast", "true");
  window.location.href = "/logout";
}

document.addEventListener("DOMContentLoaded", () => {
  // Check for logout toast flag
  if (localStorage.getItem("show_logout_toast") === "true") {
    const toastElement = document.getElementById('logout_toast');
    if (toastElement) {
      const toast = new bootstrap.Toast(toastElement);
      toast.show();
    }
    localStorage.removeItem("show_logout_toast");
  }
});