def create_css():
    return """
    .container { max-width: 1200px; margin: 0 auto; }
    .welcome-container { 
        text-align: center; 
        padding: 40px 20px; 
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .welcome-title { font-size: 3.1em; margin-bottom: 20px; } 
    .welcome-subtitle { font-size: 1.8em; color: #666; margin-bottom: 30px; } 
    .feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0; }
    .feature-card { 
        background: white; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 1.5em; 
    }
    .feature-card h3 { font-size: 1.8em; } 
    .debate-tab { 
        background: white; 
        padding: 20px; 
        border-radius: 8px;
        font-size: 1.5em; 
    }
    .debate-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .response-box { 
        background: #f8fafc; 
        padding: 15px; 
        border-radius: 6px;
        font-size: 1.5em; 
    }
    .feedback-section { 
        margin-top: 20px; 
        background: #eff6ff; 
        padding: 15px; 
        border-radius: 6px;
        font-size: 1.2em; 
    }
    .decision-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        margin: 20px 0;
        font-size: 1.2em; 
    }
    .decision-container h3 { font-size: 1.5em; }
    .decision-buttons {
        display: flex;
        gap: 20px;
        justify-content: center;
    }
    .decision-btn {
        min-width: 160px !important;
        max-width: 200px !important;
        height: 50px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1.1em !important; 
        transition: all 0.3s ease !important;
    }
    .decision-btn-selected {
        background-color: #15803d !important;
        border-color: #15803d !important;
        color: white !important;
    }
    .decision-btn-unselected {
        background-color: #e5e7eb !important;
        border-color: #d1d5db !important;
        color: #6b7280 !important;
    }
    .start-button {
        width: 200px !important;
        margin: 0 auto !important;
        font-size: 1.1em !important;
        background-color: #16a34a !important;
        border-color: #15803d !important;
        color: white !important;
    }
    .loading-button[disabled] {
        background-color: #e2e8f0 !important;
        cursor: not-allowed;
        background-color: #16a34a !important;
        border-color: #15803d !important;
        color: white !important;
    }
    .loading-button[disabled]::after {
        content: "...";
        animation: loading 1.5s infinite;
    }
    @keyframes loading {
        0% { content: "."; }
        33% { content: ".."; }
        66% { content: "..."; }
    }
    textarea, input[type="text"] {
        font-size: 1.1em !important; 
    }
    .tab-nav button {
        font-size: 1.5em !important; 
    }
    /* Added styles for labels */
    label {
        font-size: 1.1em !important; 
    }

    /* Terms Modal */
    .terms-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        max-width: 600px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
    }
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
    }
    .terms-content {
        margin-bottom: 20px;
        font-size: 1.5em;
        line-height: 1.6;
    }
    .accept-button {
        background-color: #16a34a !important;
        color: white !important;
        width: 200px !important;
    }

    /* Debater Position Boxes */
    .position-a-box textarea {
        background-color: #eff6ff !important;
        border-color: #93c5fd !important;
    }
    
    .position-b-box textarea {
        background-color: #faf5ff !important;
        border-color: #d8b4fe !important;
    }

    .position-a-box, .position-b-box {
        font-size: 1.1em;
    }

    /* Citations Section */
    .citations-section {
        margin-top: 15px;
        padding: 10px;
        background-color: #f9fafb;
        border-radius: 6px;
        border-left: 3px solid #16a34a;
    }
    .citations-section h4 {
        color: #16a34a;
        margin: 0 0 5px 0;
        font-size: 0.75em;
    }
    .citations-list {
        margin: 0;
        padding-left: 20px;
        font-size: 0.7em;
    }
    .citations-list li {
        margin-bottom: 3px;
    }
    .citations-list a {
        color: #2563eb;
        text-decoration: none;
        word-break: break-all;
    }
    .citations-list a:hover {
        text-decoration: underline;
    }
    .gradio-container .prose p, .gradio-container .markdown-body p {
        font-size: 1.2em !important;
    }
    """