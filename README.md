# WTFGEMINIJOBTASKUI: JobFit Analyzer Pro

A comprehensive job application analysis tool that evaluates your resume against job postings, provides detailed company research, and generates tailored application materials.

![JobFit Analyzer Pro](https://via.placeholder.com/1200x600/007BFF/FFFFFF?text=JobFit+Analyzer+Pro)

## 🚀 Features

- **Resume Upload**: Upload your resume (PDF, DOCX, TXT) for personalized job fit analysis
- **Deep Company Research**: Comprehensive analysis of company background, culture, and market position
- **Social Media Integration**: Automatic discovery of company LinkedIn and other social profiles
- **Salary Analysis**: Comparison of position salary with market averages
- **Employee Satisfaction Metrics**: Insights from employee reviews and company culture
- **Visual Report Format**: Clearly structured, visually appealing analysis report
- **Resume Tailoring Suggestions**: AI-powered recommendations to optimize your resume
- **Cover Letter Generation**: Custom cover letter draft based on your profile and the job

## 🛠️ Setup & Installation

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd WTFGEMINIJOBTASKUI
   ```

2. **Run the startup script:**
   ```
   ./start_app.sh
   ```

3. The script will:
   - Create a virtual environment if needed
   - Install required dependencies
   - Prompt you for your OpenRouter API key if not set
   - Start the application server

4. Access the application at: **http://localhost:8080**

## 📋 Usage

1. **Upload your resume**:
   - Click "Upload Resume" in the Candidate Profile section
   - Select your resume file (PDF, DOCX, or TXT format)
   - Wait for confirmation that your resume has been processed

2. **Enter a job posting URL**:
   - Paste the complete URL of a job listing you're interested in
   - Select analysis options (all are enabled by default)
   - Click "Analyze Job Fit"

3. **Review the analysis report**:
   - The initial analysis provides a quick assessment of your fit
   - The deep dive section includes comprehensive company research
   - The tailoring suggestions and cover letter help you customize your application

## ⚙️ Dependencies

- Python 3.6+
- Flask
- OpenAI (via OpenRouter)
- Multiple resume parsing libraries
- See `requirements.txt` for the complete list

## 🔐 API Key

This application requires an OpenRouter API key to function. You can either:
- Set it as an environment variable: `export OPENROUTER_API_KEY="your-key-here"`
- Enter it when prompted by the startup script

## 📝 License

This project is proprietary and not licensed for redistribution.

## 📬 Contact

For questions or support, please contact the repository owner.