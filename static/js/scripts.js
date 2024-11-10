// scripts.js

document.addEventListener("DOMContentLoaded", function() {
    refreshPromptList();

    // Save button event listener
    document.getElementById("saveButton").addEventListener("click", function() {
        savePrompt();
    });
});

// Function to save a new prompt using AJAX
function savePrompt() {
    const title = document.getElementById("title").value;
    const promptText = document.getElementById("prompt").value;

    if (title === "" || promptText === "") {
        alert("Title and Prompt cannot be empty.");
        return;
    }

    fetch('/save_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: title, prompt: promptText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            refreshPromptList();
            document.getElementById("title").value = "";
            document.getElementById("prompt").value = "";
        } else {
            alert("Failed to save prompt.");
        }
    });
}

// Function to fetch and update the list of saved prompts
function refreshPromptList() {
    fetch('/get_prompts')
    .then(response => response.json())
    .then(data => {
        const promptList = document.getElementById("promptList");
        promptList.innerHTML = ""; // Clear current list

        data.prompts.forEach(prompt => {
            const li = document.createElement("li");
            li.className = "py-2 border-b cursor-pointer";
            li.textContent = prompt.title;
            li.onclick = function () {
                displayPromptContent(prompt);
            };
            promptList.appendChild(li);
        });
    });
}

// Function to display selected prompt's content
function displayPromptContent(prompt) {
    alert(`Title: ${prompt.title}\nPrompt: ${prompt.text}`);
}
