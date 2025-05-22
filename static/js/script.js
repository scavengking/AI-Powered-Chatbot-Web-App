// Initialize elements
const sendButton = document.getElementById("sendButton");
const questionInput = document.getElementById("questionInput");
const question1 = document.getElementById("question1");
const question2 = document.getElementById("question2");
const solution = document.getElementById("solution");

// Secure POST method implementation
async function postData(url = "", data = {}) {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json; charset=utf-8",
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return {answer: "An error occurred while processing your request."};
    }
}

// Event listener with error handling
if (sendButton && questionInput) {
    sendButton.addEventListener("click", async () => {
        const question = questionInput.value.trim();
        if (!question) return;
        
        questionInput.value = "";
        document.querySelector(".right2").style.display = "block";
        document.querySelector(".right1").style.display = "none";

        if (question1) question1.innerHTML = question;
        if (question2) question2.innerHTML = question;

        try {
            const result = await postData("/api", {"question": question});
            if (solution && result.answer) {
                solution.innerHTML = result.answer;
            }
        } catch (error) {
            console.error("Error:", error);
            if (solution) solution.innerHTML = "Error processing your question.";
        }
    });

    // Add Enter key support
    questionInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendButton.click();
        }
    });
}
