from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import subprocess
import json
import tempfile
import logging
import uuid
from werkzeug.utils import secure_filename
from resume_parser import ResumeParser

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_candidate_profile():
    try:
        with open('candidate_profile.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading candidate profile: {e}")
        return None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/candidate-profile')
def get_candidate_profile():
    try:
        profile_data = load_candidate_profile()
        if not profile_data:
            return jsonify({
                'name': 'Error loading profile',
                'education': 'N/A',
                'experience': 'N/A'
            }), 500
            
        personal_info = profile_data.get('personalInfo', {})
        work_exp = profile_data.get('workExperience', [])
        latest_job = f"{work_exp[0]['title']} at {work_exp[0]['company']}" if work_exp else 'N/A'
        
        return jsonify({
            'name': personal_info.get('name', 'Loading...'),
            'education': personal_info.get('education', 'N/A'),
            'experience': latest_job
        })
    except Exception as e:
        logger.error(f"Error preparing profile data: {e}")
        return jsonify({
            'name': 'Error loading profile',
            'education': 'N/A',
            'experience': 'N/A'
        }), 500

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    try:
        # Generate unique filename
        file_uuid = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{file_uuid}.{extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the uploaded file
        file.save(file_path)
        logger.info(f"Resume saved to {file_path}")
        
        # Parse the resume
        parser = ResumeParser()
        profile_data = parser.parse(file_path)
        
        if not profile_data:
            return jsonify({"error": "Failed to parse resume. The file may be corrupted or in an unsupported format."}), 500
        
        # Check if there was a parsing error
        if profile_data.get("parsingError"):
            logger.warning(f"Resume parsed with errors: {profile_data.get('parsingError')}")
            # We'll still save it, but log the warning and tell the user
        
        # Save the parsed profile
        profile_path = 'candidate_profile.json'
        success = parser.save_profile(profile_data, profile_path)
        
        if not success:
            return jsonify({"error": "Failed to save profile data"}), 500
            
        # Return success response with key profile details
        personal_info = profile_data.get('personalInfo', {})
        work_exp = profile_data.get('workExperience', [])
        
        # Safely extract work experience
        try:
            if work_exp and len(work_exp) > 0:
                title = work_exp[0].get('title', 'Professional')
                company = work_exp[0].get('company', 'Company')
                latest_job = f"{title} at {company}"
            else:
                latest_job = 'No work experience found'
        except Exception:
            latest_job = 'Work experience extraction error'
        
        # Check if there was a parsing error to include in the response
        response_data = {
            "success": True,
            "message": "Resume uploaded and processed successfully",
            "profile": {
                "name": personal_info.get('name', 'Unknown'),
                "title": personal_info.get('title', 'Professional'),
                "experience": latest_job,
                "skills_count": len(profile_data.get('skills', []))
            }
        }
        
        # Include warning if there was a parsing error
        if profile_data.get("parsingError"):
            response_data["warning"] = f"Some resume data could not be parsed correctly: {profile_data.get('parsingError')}"
            response_data["message"] = "Resume processed with limited information"
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.exception(f"Error processing resume: {e}")
        return jsonify({"error": f"Error processing resume: {str(e)}"}), 500

@app.route('/analyze', methods=['POST'])
def analyze_job():
    try:
        data = request.json
        job_url = data.get('job_url')
        
        if not job_url:
            return jsonify({"error": "Job URL is required"}), 400
        
        # Check if candidate profile exists
        if not os.path.exists('candidate_profile.json'):
            return jsonify({"error": "No candidate profile found. Please upload a resume first."}), 400
        
        # Create temporary file to store output
        with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as temp:
            temp_file_path = temp.name
        
        # Run job_analyzer_cli.py with the job URL
        cmd = f"python job_analyzer_cli.py {job_url}"
        try:
            # Run the command and capture output
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            
            logger.info("Job analysis completed successfully")
            
            # Read the generated comprehensive report file
            try:
                with open('job_analysis_report_cli_COMPREHENSIVE.md', 'r') as f:
                    report_content = f.read()
                
                return jsonify({
                    "report": report_content,
                    "status": "success"
                })
            except FileNotFoundError:
                # If the report file isn't found, return the captured output
                output = result.stdout
                if output.strip():
                    return jsonify({
                        "report": output,
                        "status": "success_with_stdout"
                    })
                else:
                    return jsonify({
                        "error": "Analysis completed but no report was generated",
                        "output": result.stderr
                    }), 500
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"Analysis process error: {e.stderr}")
            return jsonify({
                "error": f"Analysis failed: {e.stderr}",
                "output": e.stdout
            }), 500
    except Exception as e:
        logger.exception(f"Server error during analysis: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)