# AI Debate System

A web-based platform where two AI debaters engage in structured debates with human judge interaction.

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone [your-repository-url]
cd ai-debate-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**
- Create a file named `SECRET` in the root directory
- Add your OpenAI API key:
```plaintext
OPENAI_API_KEY=your-api-key-here
```

4. **Run the application**
```bash
python app.py
```

5. **Access the interface**
- Open your browser
- Go to `http://127.0.0.1:7860`

## 🎯 How to Use

1. **Start a Debate**
   - Click the "Start Debate" button
   - The system will display the debate topic and positions
   - AI debaters will provide their opening arguments

2. **Judge the Debate**
   - Read both debaters' responses
   - Provide your feedback in the judge's input box
   - Click "Next Round" to proceed

3. **Debate Rounds**
   - Round 1: Opening Arguments
   - Round 2: Rebuttal Responses
   - Round 3: Closing Arguments

## 📁 Project Structure
```
ai-debate-system/
├── app.py                 # Main application
├── web_debate_manager.py  # Debate logic
├── web_css_design.py      # UI styling
├── config/
│   ├── config.yaml       # Configuration
│   └── default-prompt/   # Prompt templates
├── SECRET                # API key (create this)
└── requirements.txt      # Dependencies
```

## ⚠️ Requirements

- Python 3.8 or higher
- OpenAI API key
- Required packages (installed via requirements.txt):
  - gradio
  - openai
  - pyyaml
  - pandas

## 🤝 Need Help?

- Check if your `SECRET` file is properly formatted
- Ensure all dependencies are installed
- Verify your OpenAI API key is valid
- Make sure all config files are in place