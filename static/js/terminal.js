document.addEventListener('DOMContentLoaded', function() {
    const terminal = document.getElementById('terminal');
    const transactions = [];

    function generateRandomHash() {
        return Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
    }

    function addTransaction() {
        const newHash = generateRandomHash();
        transactions.push(newHash);
        if (transactions.length > 20) {
            transactions.shift();
        }

        updateTerminal();
    }

    function updateTerminal() {
        terminal.innerHTML = transactions.map(hash => `
            <div class="transaction">
                <span class="prompt">$</span> Blocks Hash: ${hash}
            </div>
        `).join('');

        terminal.scrollTop = terminal.scrollHeight;
    }

    setInterval(addTransaction, 1000);
});

