 document.addEventListener("DOMContentLoaded", function () {
   const messages = document.querySelectorAll(".message");

   messages.forEach((message) => {
     // Wait 3 seconds before fading out
     setTimeout(() => {
       message.classList.add("fade-out");

       // Remove the element from DOM after transition
       setTimeout(() => {
         message.remove();
       }, 1000); // match CSS transition duration
     }, 3000); // delay before fade starts
   });
 });