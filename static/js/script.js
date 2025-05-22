document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('sendButton');
    const input = document.getElementById('questionInput');
    const chatContainer = document.querySelector('.chats');

    sendBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const question = input.value.trim();
        if (!question) return;

        sendBtn.disabled = true;
        
        try {
            const response = await fetch('/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            
            if (!response.ok) throw new Error('API Error');
            
            const data = await response.json();
            window.location.reload();
            
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to send question');
        } finally {
            sendBtn.disabled = false;
            input.value = '';
        }
    });
});
