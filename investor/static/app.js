// No trading action. KILL is controlled by server-side file operations only.
document.querySelectorAll("[data-kill]").forEach((button) => {
  button.addEventListener("click", async () => {
    const response = await fetch("/api/kill", { method: "POST" });
    if (response.ok) location.reload();
  });
});
