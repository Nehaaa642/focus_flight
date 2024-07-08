// File: loadChatbot.js

document.addEventListener("DOMContentLoaded", function () {
    // Use fetch to load the HTML content
    fetch("./Users/t3/chatbot.html") // Replace "path/to/chatbot.html" with the actual path
        .then(response => response.text())
        .then(html => {
            // Create a new div element
            var chatbotContainer = document.createElement("div");

            // Set the innerHTML of the div to the loaded HTML content
            chatbotContainer.innerHTML = html;

            // Append the div to the document's body or any other desired location
            document.body.appendChild(chatbotContainer);

            // Run scripts inside the loaded HTML
            runScripts(chatbotContainer);
        })
        .catch(error => console.error("Error loading chatbot.html:", error));
});

function runScripts(container) {
    // Extract and run scripts inside the loaded HTML
    var scripts = container.querySelectorAll('script');
    scripts.forEach(script => {
        var newScript = document.createElement("script");
        newScript.text = script.text;
        container.appendChild(newScript).parentNode.removeChild(newScript);
    });
}
