// Configure AlertifyJS defaults
alertify.defaults.transition = "slide";
alertify.defaults.theme.ok = "btn btn--e-brand-b-2";
alertify.defaults.theme.cancel = "btn btn--e-transparent-brand-b-2";
alertify.defaults.glossary.title = "Notification";
alertify.defaults.delay = 5000;

// Custom styles for notifications
const style = document.createElement('style');
style.textContent = `
    .alertify-notifier {
        top: 20px;
        right: 20px;
    }
    .alertify-notifier .ajs-message {
        border-radius: 4px;
        padding: 15px 20px;
        font-family: 'Open Sans', sans-serif;
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .alertify-notifier .ajs-message.ajs-success {
        background: #4CAF50;
        color: white;
    }
    .alertify-notifier .ajs-message.ajs-error {
        background: #f44336;
        color: white;
    }
    .alertify-notifier .ajs-message.ajs-warning {
        background: #ff9800;
        color: white;
    }
    .alertify-notifier .ajs-message.ajs-info {
        background: #2196F3;
        color: white;
    }
`;
document.head.appendChild(style);

// Function to display messages
function displayMessage(message, type = 'info') {
    switch(type) {
        case 'success':
            alertify.success(message);
            break;
        case 'error':
            alertify.error(message);
            break;
        case 'warning':
            alertify.warning(message);
            break;
        default:
            alertify.message(message);
    }
}

// Function to handle Django messages
function handleDjangoMessages() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        const type = message.classList.contains('alert-success') ? 'success' :
                    message.classList.contains('alert-danger') ? 'error' :
                    message.classList.contains('alert-warning') ? 'warning' : 'info';
        displayMessage(message.textContent.trim(), type);
        message.remove(); // Remove the original message after displaying
    });
}

// Initialize message handling when DOM is loaded
document.addEventListener('DOMContentLoaded', handleDjangoMessages); 