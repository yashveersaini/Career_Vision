// Handle form submission for job prediction
document.getElementById('submitBtn')?.addEventListener('click', async () => {
    const skillsInput = document.getElementById('skillsInput');
    const skillsError = document.getElementById('skillsError');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const skills = skillsInput.value.split(',').map(skill => skill.trim());

    if (!skillsInput.value.trim()) {
        skillsError.style.display = 'block';
        return;
    }

    skillsError.style.display = 'none';
    loadingSpinner.style.display = 'block';  // Show loading spinner after validation
    const interest = document.getElementById('interest').value;

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ skills, interest })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const results = await response.json();
        loadingSpinner.style.display = 'none';  // Hide loading spinner
        displayResults(results);
    } catch (error) {
        console.error('Error:', error);
        loadingSpinner.style.display = 'none';  // Hide loading spinner on error
        alert('An error occurred while processing your request.');
    }
});

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    const suggestedJobs = document.getElementById('suggestedJobs');
    const referencesDiv = document.getElementById('references');

    // Clear previous results
    referencesDiv.innerHTML = '';

    // Display suggested jobs
    suggestedJobs.textContent = `Suggested jobs: ${results.map(result => result.role).join(', ')}`;

    // Display videos for each role
    results.forEach(result => {
        const videoContainer = document.createElement('div');
        videoContainer.classList.add('video-container');

        videoContainer.innerHTML = `
            <h4>For ${result.role}</h4>
            <div class="row">
                ${result.video_links.map(link => `
                    <div class="col-md-6">
                        <iframe src="${link}" 
                                frameborder="0" 
                                allowfullscreen>
                        </iframe>
                    </div>
                `).join('')}
            </div>
        `;

        referencesDiv.appendChild(videoContainer);
    });

    // Show results and chat button
    resultsDiv.style.display = 'block';
    document.getElementById('chatButton').style.display = 'block';
}

// Chat functionality
function sendMessage() {
    const inputField = document.getElementById("message-input");
    const message = inputField.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");

    // Add user message
    appendMessage(message, true);
    inputField.value = "";

    // Show loading indicator
    const loadingDiv = document.createElement("div");
    loadingDiv.classList.add("message", "bot-message", "loading-message");
    loadingDiv.innerHTML = '<span class="loading"></span><span class="loading"></span><span class="loading"></span>';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send to backend
    fetch('/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        chatBox.removeChild(loadingDiv);
        // Add bot response
        appendMessage(data.response, false);
    })
    .catch(error => {
        console.error("Error:", error);
        chatBox.removeChild(loadingDiv);
        appendMessage("Sorry, I encountered an error. Please try again.", false);
    });
}

function appendMessage(text, isUser) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", isUser ? "user-message" : "bot-message");
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Handle enter key in chat input
document.getElementById("message-input")?.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});