// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Get all "Open Popup" buttons (for each post)
    const openPopupButtons = document.querySelectorAll(".button-delete");

    openPopupButtons.forEach(button => {
        button.addEventListener("click", () => {
            const postId = button.id.replace('openPopup', ''); // Get the post ID
            const popup = document.getElementById("popupContainer" + postId); // Get the corresponding popup
            popup.style.display = "block"; // Show the popup
        });
    });

    // Get all "Close" buttons (for each post)
    const closePopupButtons = document.querySelectorAll(".closePopup");

    closePopupButtons.forEach(button => {
        button.addEventListener("click", () => {
            const postId = button.id.replace('closePopup', ''); // Get the post ID
            const popup = document.getElementById("popupContainer" + postId); // Get the corresponding popup
            popup.style.display = "none"; // Hide the popup
        });
    });
});

