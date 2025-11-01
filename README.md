# DNIT_PRO006
Pavement Severity Index (IGG) Calculator (DNIT PRO-006)
This is a web application built as a final project for Harvard's CS50. It serves as an engineering tool to automate the calculation of the Global Severity Index (IGG, or Índice de Gravidade Global), a key metric used in Brazil to assess the condition of highway pavements.

The calculation logic is based on the official DNIT PRO-006 standard. https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/ipr/coletanea-de-normas/coletanea-de-normas/procedimento-pro/dnit006_2003_pro.pdf

What is this?
In transportation engineering, assessing pavement quality involves manually inspecting 20-meter stations of a highway, noting various types of defects (cracks, potholes, etc.). These defects are then manually entered into complex spreadsheets to calculate the IGG. This process is slow, repetitive, and prone to human error.
This project automates that entire workflow.

What it does
The application provides a simple web interface where a user can:
1. Upload a standardized road inspection spreadsheet (in .xlsx format).
2. Specify the Mode of Calculation ("Intercalado", as per the standard, or "Somado", combining both lanes).
3. Specify the Inventory Type (Pista Simples, Pista Dupla, Terceira Faixa).
4. Specify the starting row where the data begins (to accommodate variable-sized headers).

The backend then processes the entire sheet, reading defect data (for both Left and Right lanes) for every 20-meter station. It calculates the Individual Severity Index (IGI) for each station and aggregates them into the final Global Severity Index (IGG) for each 1km segment.
Finally, it visualizes the results on a report page, featuring:
An interactive chart showing the IGI for every station (the "pavement electrocardiogram").
A summary chart showing the final IGG for each 1km segment.
A summary table of the final IGG values.

Technologies Used
Backend: Python with the Flask web framework.
Data Processing: Pandas library for reading and parsing the Excel files.
Database: SQLite for storing the processed data from each station.
Visualization: Plotly for generating interactive charts.
Frontend: Standard HTML, CSS, and Jinja2 templating.

Project Ambition
The primary goal is to transform a time-consuming, manual, and error-prone engineering task into a fast, reliable, and automated process. This tool aims to save engineers significant time and deliver clear, actionable, and verifiable pavement quality reports from a single file upload.

Current Stage
As of November 01, 2025, the project is in the development phase.

[x] Step 1: Project setup and environment (Done)

[x] Step 2: Basic Flask server and UI (Done)

[x] Step 3: File upload functionality (Done)

[x] Step 4: Database schema design (Done)

[x] Step 5: Core calculation logic (PRO-006) (Done)

[x] Step 6: Report and visualization generation (Done)

Known Issues and Future Improvements
This project serves as a robust foundation. After submission, I plan to expand its capabilities with the following features:

* Exportable Calculation Sheets: Generate and export a detailed "calculation sheet" for each segment, matching the official format required by the standard.
* Homogeneous Segments: Add an option for the user to define custom homogeneous segments (e.g., based on pavement type or construction date) instead of using the default 1km segments.
* Email Reports: Implement a feature to ask for the user's email and send the complete report (with graphs and data) as an attachment.
* UI/UX Enhancements: Refine the index.html and relatorio.html pages to create a more polished, modern, and visually appealing user experience.
