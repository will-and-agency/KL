# Municipality Energy & Building Dashboard

## 📖 Project Overview
This project is a data visualization dashboard built with **Python** and **Dash**. It aggregates, processes, and visualizes energy consumption, building maintenance, and carbon data for three Danish municipalities:

* **Faaborg-Midtfyn**
* **Frederiksberg**
* **Randers**

The dashboard allows users to explore data through interactive plots, offering insights into electricity, heating, and water usage, as well as CO2 emissions and building operations.

---

## 🚀 Getting Started

Follow these steps to set up the project on your local machine.

### 1. Prerequisites
Ensure you have the following installed:
* **Python 3.10+** (Check with `python --version`)
* **Git** (Check with `git --version`)
* Ensure you have **Anaconda** or **Miniconda** installed.

### 2. Clone the Repository
Open your terminal or command prompt and run:

```bash
git clone <repository_url>
cd <repository_folder_name>
```
### 3. Environment Setup
This project uses a pre-defined Anaconda environment. To set it up, open your Anaconda Prompt or terminal and run:
Windows:
```bash
conda env create -f environment.yml

# Activate the environment
conda activate kl_env
```

## 📂 Data Structure
The application requires a specific folder structure to locate Excel and CSV files correctly. Ensure your local data/ directory matches this layout exactly:

```plaintext
root/
├── data/
│   ├── faaborg&midtfyn/
│   │   ├── DKV.xlsx - Uglen - Forbrug 2022-24.csv
│   │   ├── Forbrugsoplysninger FM.xlsx - Energi.csv
│   │   └── ... (other Faaborg CSVs)
│   │
│   ├── frederiksberg/
│   │   ├── Bygningsinfo - Dalux.xlsx - Data.csv
│   │   ├── Dataoversigt Frb. kommune.xlsx - Ark1.csv
│   │   └── ... (other Frederiksberg CSVs)
│   │
│   └── randers/
│       ├── Energy Projects/
│       ├── Dalux/
│       └── EnergyKey/
│
├── faaborg_carbon_data.json
├── frb_processed.json
├── randers_processed.json
└── mapping.json
```
[!IMPORTANT]

The app will fail to load if these folders or key files are missing or incorrectly named.

## 🏃‍♂️ Running the Application
Activate your virtual environment (if not already active).

Run the app:

```bash
python app.py
```
## 🧩 Codebase Structure

| File                        | Folder,Description                                                                     |
| --------------------------- | -------------------------------------------------------------------------------------- |
| app.py                      | "Entry Point. The main Dash application file. Defines layout, routing, and callbacks." |
| data_processing.py          | Data cleaning/transformation for Faaborg-Midtfyn and shared utilities.                 |
| data_processing_fbr.py      | Data processing logic for Frederiksberg.                                               |
| data_processing_randers.py  | Data processing logic for Randers.                                                     |
| plots.py                    | Plotly figure generation for Faaborg-Midtfyn.                                          |
| plots_fbr.py                | Plotly figure generation for Frederiksberg.                                            |
| analysis_generator.py       | Generates text-based insights and summary components.                                  |
| assets/                     | "Static files (CSS, JS) automatically served by Dash."                                 |


## 🛠 Troubleshooting
* **ModuleNotFoundError**: You likely forgot to activate the virtual environment or install requirements.txt.

* **FileNotFoundError**: Check the data/ folder. The folder names (faaborg&midtfyn, frederiksberg, randers) must match exactly, including casing.

* **Empty Graphs**: This often happens if the input CSV format has changed (e.g., column headers renamed), causing the data processor to filter out all rows.
View in Browser: Open http://127.0.0.1:8050/ in your web browser.
