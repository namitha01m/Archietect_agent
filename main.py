import sys
import requests
import base64
from io import BytesIO
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTextEdit, QLabel, QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PIL import ImageGrab

# The URL for the local Ollama API. 
OLLAMA_API_URL = "http://localhost:11434/api/generate"

class CoPilotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hackathon Co-Pilot")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Agent 1: The Architect
        self.project_label = QLabel("Step 1: Enter your high-level project idea:")
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("e.g., 'A simple weather app using Python'")
        layout.addWidget(self.project_label)
        layout.addWidget(self.project_input)
        self.architect_button = QPushButton("Architect Project Plan (Llama 3)")
        self.architect_button.clicked.connect(self.act_as_architect)
        layout.addWidget(self.architect_button)
        
        layout.addSpacing(20)

        # Agent 2: The Coder
        self.coder_label = QLabel("Step 2: Enter a specific task for The Coder:")
        self.coder_input = QLineEdit()
        self.coder_input.setPlaceholderText("e.g., 'Write a Python function to get weather data from an API'")
        layout.addWidget(self.coder_label)
        layout.addWidget(self.coder_input)
        self.coder_button = QPushButton("Write Code (Gemma 3n)")
        self.coder_button.clicked.connect(self.act_as_coder)
        layout.addWidget(self.coder_button)
        
        layout.addSpacing(20)

        # Agent 3: The Debugger
        self.debugger_label = QLabel("Step 3: Capture an error for The Debugger:")
        layout.addWidget(self.debugger_label)
        self.debugger_button = QPushButton("Debug Error (Gemma 3n)")
        self.debugger_button.clicked.connect(self.act_as_debugger)
        layout.addWidget(self.debugger_button)

        self.output_label = QLabel("Co-Pilot's Response:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_label)

        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.addWidget(self.output_text)
        layout.addLayout(self.scroll_layout)

        self.setLayout(layout)

    def act_as_architect(self):
        project_idea = self.project_input.text()
        if not project_idea:
            self.output_text.setText("Please enter a project idea.")
            return

        self.architect_button.setEnabled(False)
        self.output_text.setText("Architect is breaking down the project idea...")
        QApplication.processEvents()

        try:
            system_prompt = (
                "You are an expert AI Architect and Project Manager. "
                "The user will provide a high-level project idea. "
                "Your task is to break it down into a numbered list of concrete, actionable steps for a hackathon team to follow. "
                "Be detailed and provide a clear plan."
            )
            full_prompt = f"{system_prompt}\n\nProject Idea: {project_idea}"

            data = {
                "model": "llama3:8b",
                "prompt": full_prompt,
                "stream": False
            }
            
            response = requests.post(OLLAMA_API_URL, json=data)
            response.raise_for_status()
            
            response_json = response.json()
            plan_response = response_json.get("response", "No response from AI.")
            self.output_text.setText(plan_response)
        
        except requests.exceptions.RequestException as e:
            self.output_text.setText(f"Error communicating with Ollama: {e}. Is your Ollama server running with Llama 3?")
        except Exception as e:
            self.output_text.setText(f"An unexpected error occurred: {e}")
        
        finally:
            self.architect_button.setEnabled(True)

    def act_as_coder(self):
        task_idea = self.coder_input.text()
        if not task_idea:
            self.output_text.setText("Please enter a specific task for The Coder.")
            return

        self.coder_button.setEnabled(False)
        self.output_text.setText("Coder is writing the code...")
        QApplication.processEvents()

        try:
            system_prompt = (
                "You are an expert AI Coder. "
                "The user will provide a specific task. "
                "Your task is to write a clean, well-commented code snippet that solves the task. "
                "Provide only the code and nothing else. Do not provide explanations or extra text."
            )
            full_prompt = f"{system_prompt}\n\nTask: {task_idea}"

            data = {
                "model": "gemma3n:e4b",
                "prompt": full_prompt,
                "stream": False
            }
            
            response = requests.post(OLLAMA_API_URL, json=data)
            response.raise_for_status()
            
            response_json = response.json()
            code_response = response_json.get("response", "No response from AI.")
            self.output_text.setText(code_response)
        
        except requests.exceptions.RequestException as e:
            self.output_text.setText(f"Error communicating with Ollama: {e}. Is your Ollama server running with Gemma 3n?")
        except Exception as e:
            self.output_text.setText(f"An unexpected error occurred: {e}")
        
        finally:
            self.coder_button.setEnabled(True)

    def act_as_debugger(self):
        self.debugger_button.setEnabled(False)
        self.output_text.setText("Debugger is capturing the screen and analyzing the error...")
        QApplication.processEvents()

        try:
            # Capture the screen
            screenshot = ImageGrab.grab()
            
            # Convert image to base64
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # --- Prompt Engineering for The Debugger Agent ---
            # We explicitly instruct Gemma to act as an expert debugger
            system_prompt = (
                "You are an expert AI Debugger. The user has provided a screenshot of a bug or an error. "
                "Analyze the image and provide a detailed, actionable solution. "
                "Your response should be a clear explanation of the problem and the steps to fix it."
            )

            data = {
                "model": "gemma3n:e4b",
                "prompt": system_prompt,
                "images": [img_str],
                "stream": False
            }
            
            response = requests.post(OLLAMA_API_URL, json=data)
            response.raise_for_status()
            
            response_json = response.json()
            debug_response = response_json.get("response", "No response from AI.")
            self.output_text.setText(debug_response)
        
        except requests.exceptions.RequestException as e:
            self.output_text.setText(f"Error communicating with Ollama: {e}. Is your Ollama server running with Gemma 3n?")
        except Exception as e:
            self.output_text.setText(f"An unexpected error occurred: {e}")
        
        finally:
            self.debugger_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoPilotApp()
    window.show()
    sys.exit(app.exec())