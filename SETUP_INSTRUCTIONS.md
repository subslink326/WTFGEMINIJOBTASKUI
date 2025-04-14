# WTFGEMINIJOBTASKUI Setup Instructions

## What's in this project?

This project contains:

1. A web-based UI (`static/index.html`) using Tailwind CSS and FontAwesome
2. A Flask backend (`app.py`) that serves the UI and processes job analysis requests
3. The job analyzer script (`job_analyzer_cli.py`) that performs the actual analysis
4. Your candidate profile data (`candidate_profile.json`)
5. Requirements file (`requirements.txt`) listing all dependencies
6. Start script (`start_app.sh`) to easily run the application

## Quick Start

1. Set your OpenRouter API key:
   ```
   export OPENROUTER_API_KEY="your-api-key-here"
   ```

2. Run the application:
   ```
   ./start_app.sh
   ```

3. Open http://localhost:8080 in your browser

## How It Works

1. The UI allows you to enter a job posting URL
2. When you click "Analyze Job Fit", the URL is sent to the Flask backend
3. The backend runs `job_analyzer_cli.py` with the URL as an argument
4. The script analyzes the job posting using AI and generates a report
5. The report is sent back to the UI and displayed in a formatted way

## Customization

- To update your candidate profile, edit `candidate_profile.json`
- To modify the UI, edit `static/index.html`
- To change the Flask backend behavior, edit `app.py`
- To modify the analysis logic, edit `job_analyzer_cli.py` (advanced)

## Troubleshooting

- If you see "Error loading profile", make sure `candidate_profile.json` is in the correct format
- If analysis fails, check your OpenRouter API key and internet connection
- For more detailed logs, check the terminal where you're running the application