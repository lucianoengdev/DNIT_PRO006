# DNIT_PRO006
Pavement Severity Index (IGG) Calculator (DNIT PRO-006)
This is a web application built as a final project for Harvard's CS50. It serves as an engineering tool to automate the calculation of the Global Severity Index (IGG, or Índice de Gravidade Global), a key metric used in Brazil to assess the condition of highway pavements.

The calculation logic is based on the official DNIT PRO-006 standard.

What is this?
In transportation engineering, assessing pavement quality involves manually inspecting 20-meter stations of a highway, noting various types of defects (cracks, potholes, etc.). These defects are then manually entered into complex spreadsheets to calculate the IGG. This process is slow, repetitive, and prone to human error.

This project automates that entire workflow.

What it does
The application provides a simple web interface where a user can:

Upload a standardized road inspection spreadsheet (in .xlsx format).

Specify the starting row where the data begins (to accommodate variable-sized headers).

The backend then processes the entire sheet, reading defect data (for both Left and Right lanes) for every 20-meter station. It calculates the Individual Severity Index (IGI) for each station and aggregates them into the final Global Severity Index (IGG) for each 1km segment.

Finally, it visualizes the results on a report page, featuring:

An interactive chart showing the IGI for every station (the "pavement electrocardiogram").

A summary chart showing the final IGG for each 1km segment.

A summary table of the final IGG values.

Technologies Used
Backend: Python 3 with the Flask web framework.

Data Processing: Pandas library for reading and parsing the Excel files.

Database: SQLite for storing the processed data from each station.

Visualization: Plotly for generating interactive charts.

Frontend: Standard HTML, CSS, and Jinja2 templating.

Project Ambition
The primary goal is to transform a time-consuming, manual, and error-prone engineering task into a fast, reliable, and automated process. This tool aims to save engineers significant time and deliver clear, actionable visualizations of pavement quality from a single file upload.

Current Stage
As of October 30, 2025, the project is in the development phase.

[x] Step 1: Project setup and environment (Done)

[x] Step 2: Basic Flask server and UI (Done)

[x] Step 3: File upload functionality (Done)

[x] Step 4: Database schema design (Done)

[ ] Step 5: Core calculation logic (PRO-006) (In Progress)

[ ] Step 6: Report and visualization generation

Known Issues and Future Improvements
I will fill it when I done the steps up and start to implementations
