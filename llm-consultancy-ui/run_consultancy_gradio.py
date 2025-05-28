from dotenv import load_dotenv
from consultation_ui_class import ConsultationUI
import sys
load_dotenv()

def main():
    try:
        ui = ConsultationUI()
        interface = ui.create_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860
        )
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()