def create_css():
    return """
    /* Global Reset and Variables */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #16a34a;
        --neutral-900: #111827;
        --neutral-800: #1f2937;
        --neutral-700: #374151;
        --neutral-100: #f3f4f6;
        --neutral-50: #f8fafc;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --radius-lg: 12px;
        --radius-md: 8px;
    }

    /* Main Container */
    .contain {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    /* Header Styling */
    .header-text {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--neutral-900);
        text-align: center;
        margin: 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--neutral-100);
        letter-spacing: -0.025em;
    }

    .header-text span {
        font-size: 2.75rem;
        margin-right: 0.5rem;
    }

    /* Debate Header */
    .debate-header {
        background: white;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        margin-bottom: 2rem;
    }

    /* Statement Box */
    .statement-box {
        background: var(--neutral-50);
        padding: 1.5rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--neutral-100);
        margin-bottom: 1.5rem;
    }

    /* Positions Grid */
    .positions-section {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin-top: 1.5rem;
    }

    .position-box {
        background: var(--neutral-50);
        padding: 1.5rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--neutral-100);
        transition: transform 0.2s ease;
    }

    .position-box:hover {
        transform: translateY(-2px);
    }

    .position-a {
        border-left: 4px solid var(--primary-color);
    }

    .position-b {
        border-left: 4px solid var(--secondary-color);
    }

    /* Typography */
    .statement-box strong,
    .position-box strong {
        font-size: 1rem;
        font-weight: 600;
        color: var(--neutral-800);
        margin-right: 0.5rem;
    }

    .answer-text {
        font-size: 1rem;
        line-height: 1.6;
        color: var(--neutral-700);
    }

    /* Debate Containers */
    .debater-container {
        background: white;
        border-radius: var(--radius-lg);
        border: 1px solid var(--neutral-100);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s ease;
    }

    .debater-container:hover {
        box-shadow: var(--shadow-md);
    }

    /* Round Indicators */
    .round-indicator {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--neutral-800);
        margin: 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--neutral-100);
    }

    /* Textboxes */
    .textbox-container label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--neutral-800) !important;
        margin-bottom: 0.75rem !important;
    }

    .textbox-container textarea {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
        border: 1px solid var(--neutral-100) !important;
        border-radius: var(--radius-md) !important;
        background: white !important;
        min-height: 160px !important;
        resize: vertical !important;
        transition: border-color 0.2s ease !important;
    }

    .textbox-container textarea:focus {
        border-color: var(--primary-color) !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important;
    }

    /* Judge Feedback */
    .feedback-box {
        background: white !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--neutral-100) !important;
        margin: 1rem 0 !important;
    }

    .feedback-box label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--neutral-800) !important;
    }

    .feedback-box textarea {
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
        transition: border-color 0.2s ease !important;
    }

    .judge-history {
        background: var(--neutral-50) !important;
        border-left: 4px solid #818cf8 !important;
        font-size: 1rem !important;
    }

    /* Buttons */
    .button-row {
        display: flex;
        justify-content: center;
        margin: 1.5rem 0;
    }

    .button-primary {
        background: var(--primary-color) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: var(--radius-md) !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    .button-primary:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px) !important;
    }

    .button-primary:disabled {
        opacity: 0.7 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .positions-section {
            grid-template-columns: 1fr;
        }

        .header-text {
            font-size: 2rem !important;
        }

        .round-indicator {
            font-size: 1.1rem;
        }

        .contain {
            padding: 1rem;
        }
    }
"""