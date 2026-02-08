function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    const messagesDiv = document.getElementById('messages');
    
    // Adicionar mensagem do usuário
    const userMsg = document.createElement('div');
    userMsg.style.cssText = 'background: #667eea; color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px;';
    userMsg.textContent = `Você: ${message}`;
    messagesDiv.appendChild(userMsg);
    
    // Simular resposta do bot
    setTimeout(() => {
        const botMsg = document.createElement('div');
        botMsg.style.cssText = 'background: #e0e0e0; padding: 10px; border-radius: 10px; margin-bottom: 10px;';
        botMsg.textContent = `Bot: Mensagem recebida - "${message}"`;
        messagesDiv.appendChild(botMsg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }, 500);
    
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

document.getElementById('message-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
