# Automation Scripts

## Overview
This repository contains various automation scripts designed to streamline tasks related to license management and tender updates.

## Folder Structure
- **License automation**: Automates the process of checking certificate expirations and sending email reminders.
- **Dailytenderupdate**: Scrapes tender information from a government website and sends email notifications for new tenders.

## Requirements
- Python 3.x
- Required libraries (install using pip):
  - For License automation: `schedule`
  - For Daily tender update: `selenium`, `beautifulsoup4`

## Installation
1. Clone this repository or download the scripts.
2. Install the required libraries for each script:
   - For License automation:
     ```bash
     pip install schedule
     ```
   - For Daily tender update:
     ```bash
     pip install selenium beautifulsoup4
     ```

## Usage
Refer to the individual README files in each folder for specific usage instructions.

## Running with Task Scheduler

To automate the execution of these scripts, you can use Windows Task Scheduler. Here's how to set it up:

1. Open Task Scheduler (search for it in the Start menu).
2. Click on "Create Basic Task" in the right panel.
3. Name your task (e.g., "License Automation" or "Daily Tender Update").
4. Choose when you want the task to start (e.g., daily, weekly).
5. Select "Start a program" as the action.
6. In the "Program/script" field, enter the path to your Python executable (e.g., `C:\Python39\python.exe`).
7. In the "Add arguments" field, enter the full path to your script (e.g., `C:\Scripts\license_automation.py`).
8. In the "Start in" field, enter the directory containing your script.
9. Review your settings and click "Finish".

For scripts that need to run continuously (like those using the `schedule` library):
1. Follow steps 1-8 above.
2. After clicking "Finish", right-click on your newly created task and select "Properties".
3. In the "Settings" tab, check the box for "Run task as soon as possible after a scheduled start is missed".
4. Set "Stop the task if it runs longer than" to a value that exceeds your intended run time (e.g., 1 day).
5. Click "OK" to save the changes.

Make sure your scripts are designed to run indefinitely if you want them to keep running after execution.

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any improvements or suggestions.
