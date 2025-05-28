
def create_css() -> str:
    """Creates CSS styles for the application."""
    return """
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .terms-modal {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        width: 80%;
        max-width: 800px;
        max-height: 80vh;
        overflow-y: auto;
    }
    .terms-content {
        margin-bottom: 20px;
        font-size: 1.1em;
        line-height: 1.6;
    }
    .accept-button {
        background-color: #16a34a !important;
        color: white !important;
        width: 200px !important;
    }
    .start-button {
        width: 200px !important;
        margin: 0 auto !important;
        font-size: 1.1em !important;
        background-color: #16a34a !important;
        border-color: #15803d !important;
        color: white !important;
    }
    .loading-text-start::before {
        content: "Starting consultation";
        animation: loading-dots-start 1.5s infinite;
    }
    
    .loading-text-submit::before {
        content: "Setting up next round";
        animation: loading-dots-submit 1.5s infinite;
    }
    
    @keyframes loading-dots-start {
        0% { content: "Starting consultation"; }
        25% { content: "Starting consultation."; }
        50% { content: "Starting consultation.."; }
        75% { content: "Starting consultation..."; }
    }
    
    @keyframes loading-dots-submit {
        0% { content: "Setting up next round"; }
        25% { content: "Setting up next round."; }
        50% { content: "Setting up next round.."; }
        75% { content: "Setting up next round..."; }
    }
    .status-text {
            font-size: 1.4em !important;
            font-weight: 600 !important;
        }

    .large-text-box label {
        font-size: 1.1em !important;
    }

    .large-button {
        font-size: 1.2em !important;
        padding: 12px 24px !important;
        height: auto !important;
    }
    """