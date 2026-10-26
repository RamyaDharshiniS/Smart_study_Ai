SMART STUDY AI — INSTALLATION (Windows + VS Code)

Files in this project:
- app.py: complete Streamlit app
- style.css: black/charcoal theme with electric blue and lime accents
- requirements.txt: Python dependency list

Run:
1. Extract this ZIP into a folder such as Desktop\SmartStudyAI.
2. Open that folder in VS Code (File > Open Folder).
3. Open Terminal > New Terminal.
4. Create a virtual environment (skip if you already have one):
   py -m venv .venv
5. Activate it:
   .\.venv\Scripts\Activate.ps1
   If activation is blocked, use .\.venv\Scripts\python.exe in the next commands.
6. Install:
   python -m pip install -r requirements.txt
7. Run:
   python -m streamlit run app.py
8. If no browser opens, visit http://localhost:8501.

The photos load from Unsplash and require an internet connection.
This version keeps subjects in Streamlit session state for the active session; it does not yet save data permanently.
The study coach uses predefined general study tips and simple rules. It is not a live AI model and does not know your exact syllabus automatically.
