"""
Resume Parser Module - Extracts information from uploaded resumes and creates a candidate profile
"""

import os
import json
import re
import tempfile
from datetime import datetime
import logging

# Try importing optional libraries for parsing different file types
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text as pdf_extract_text
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """Parses resume files and creates a candidate profile JSON"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.pdf', '.docx']
        
    def parse(self, file_path):
        """
        Parse a resume file and extract structured information
        Returns a dictionary with the parsed information
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
                
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in self.supported_extensions:
                logger.error(f"Unsupported file type: {file_ext}")
                return None
                
            # Extract text based on file type
            text = None
            if file_ext == '.pdf':
                text = self._extract_pdf_text(file_path)
            elif file_ext == '.docx':
                text = self._extract_docx_text(file_path)
            else:  # Assume .txt
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                except UnicodeDecodeError:
                    # Try with a different encoding if utf-8 fails
                    with open(file_path, 'r', encoding='latin-1') as f:
                        text = f.read()
                        
            if not text:
                logger.error(f"Failed to extract text from {file_path}")
                # Return default empty profile instead of None
                return self._create_default_profile()
                
            # Parse the text into structured data
            structured_data = self._extract_information(text)
            return structured_data
        except Exception as e:
            logger.exception(f"Error parsing resume: {e}")
            # Return a default profile with error information
            return self._create_default_profile(error=str(e))
            
    def _create_default_profile(self, error=None):
        """Create a default profile when parsing fails"""
        current_date = datetime.now().strftime("%B, %d %Y")
        default_profile = {
            "personalInfo": {
                "name": "Resume Upload Error" if error else "Unknown Candidate",
                "title": "Professional",
                "location": "Unknown Location",
                "contact": {
                    "email": None,
                    "phone": None,
                    "website": None,
                    "linkedin": None
                }
            },
            "summary": f"Error parsing resume: {error}" if error else "No summary could be extracted from the resume.",
            "skills": ["No skills extracted"],
            "workExperience": [
                {
                    "title": "Professional",
                    "company": "Previous Employment",
                    "location": None,
                    "dates": "Unknown",
                    "description": ["No work experience details could be extracted."]
                }
            ],
            "projects": [],
            "interests": [],
            "references": [],
            "documentDate": current_date,
            "parsingError": error
        }
        return default_profile
        
    def _extract_pdf_text(self, file_path):
        """Extract text from PDF files"""
        if PDFMINER_AVAILABLE:
            try:
                return pdf_extract_text(file_path)
            except Exception as e:
                logger.error(f"Error extracting text with pdfminer: {e}")
        
        if PDF_AVAILABLE:
            try:
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except Exception as e:
                logger.error(f"Error extracting text with PyPDF2: {e}")
                
        logger.error("No PDF parsing library available")
        return None
        
    def _extract_docx_text(self, file_path):
        """Extract text from DOCX files"""
        if not DOCX_AVAILABLE:
            logger.error("python-docx library not available")
            return None
            
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return None
            
    def _extract_information(self, text):
        """
        Extract structured information from resume text
        This is a simplified extraction - for production use, consider using NLP libraries
        """
        info = {
            "personalInfo": {
                "name": self._extract_name(text),
                "title": self._extract_title(text),
                "location": self._extract_location(text),
                "contact": self._extract_contact_info(text)
            },
            "summary": self._extract_summary(text),
            "skills": self._extract_skills(text),
            "workExperience": self._extract_work_experience(text),
            "projects": self._extract_projects(text),
            "interests": [],
            "references": [],
            "documentDate": datetime.now().strftime("%B, %d %Y")
        }
        return info
        
    def _extract_name(self, text):
        """Extract candidate name from text"""
        # Simple heuristic: first line is often the name
        lines = text.strip().split('\n')
        for line in lines[:3]:  # Check first 3 lines
            # Name is usually short and capitalized
            cleaned = line.strip()
            if len(cleaned) > 0 and len(cleaned.split()) <= 4:
                return cleaned
        return "Unknown Name"
        
    def _extract_title(self, text):
        """Extract professional title"""
        title_patterns = [
            r'(?:^|\n)([A-Za-z\s]{5,40}?)(?:\n|$)',  # Title on its own line
            r'(?:^|\n).*?\|\s*([A-Za-z\s&]{5,40}?)(?:\s*\||$)',  # Title between pipes
            r'(?:SUMMARY|PROFILE|OBJECTIVE)[^\n]*?\n+([A-Za-z\s]{5,40}?)\s'  # Title after summary heading
        ]
        
        # Check for title after name
        lines = text.strip().split('\n')
        if len(lines) > 1:
            potential_title = lines[1].strip()
            if len(potential_title) > 0 and len(potential_title.split()) <= 5:
                return potential_title
        
        # Try patterns
        for pattern in title_patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
                
        return "Professional"
        
    def _extract_location(self, text):
        """Extract location information"""
        # Look for common location patterns
        location_patterns = [
            r'(?:^|\n)(?:Address|Location):\s*(.+?)(?:\n|$)',
            r'(?:^|\n)([A-Za-z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?)(?:\n|$)',  # City, State ZIP
            r'(?:^|\n)((?:[A-Za-z\s\-\'\.]+,\s+){1,2}(?:USA|Canada|United States))(?:\n|$)'  # City, State, Country
        ]
        
        for pattern in location_patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
                
        return "Location Unknown"
        
    def _extract_contact_info(self, text):
        """Extract contact information"""
        contact = {
            "email": None,
            "phone": None,
            "website": None,
            "linkedin": None
        }
        
        # Find email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact["email"] = email_match.group(0)
            
        # Find phone
        phone_patterns = [
            r'(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US/CA: (123) 456-7890
            r'\d{3}[\s.-]\d{3}[\s.-]\d{4}'  # 123-456-7890
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact["phone"] = phone_match.group(0)
                break
                
        # Find LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group(0)
            
        # Find website
        website_patterns = [
            r'(?:https?://)?(?:www\.)?[\w\-]+\.(?:com|org|net|io|dev)(?:/[\w\-]*)*',
            r'(?:^|\s)([\w\-]+\.(?:com|org|net|io|dev)(?:/[\w\-]*)*)(?:\s|$)'
        ]
        for pattern in website_patterns:
            website_match = re.search(pattern, text)
            if website_match:
                match_text = website_match.group(0) if pattern.startswith('(?:https') else website_match.group(1)
                if match_text and not ("linkedin" in match_text.lower()):
                    contact["website"] = match_text.strip()
                    break
                
        return contact
        
    def _extract_summary(self, text):
        """Extract professional summary"""
        summary_patterns = [
            r'(?:SUMMARY|PROFILE|OBJECTIVE)[:\s]*\n+(.+?)\n\n',
            r'(?:SUMMARY|PROFILE|OBJECTIVE)[:\s]*(.+?)(?=\n\n|\n[A-Z]+|\Z)'
        ]
        
        for pattern in summary_patterns:
            matches = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                summary = matches.group(1).strip()
                # Clean up the summary
                summary = re.sub(r'\s+', ' ', summary)
                if len(summary) > 30:  # Reasonable length for a summary
                    return summary
                    
        # Fallback: try to find the first paragraph after the contact info
        paragraphs = re.split(r'\n\s*\n', text)
        for i, para in enumerate(paragraphs):
            if i > 0 and len(para.strip()) > 100:  # Skip header, find substantive paragraph
                return para.strip()
                
        return "No summary provided"
        
    def _extract_skills(self, text):
        """Extract skills from the resume"""
        skills = []
        
        # Look for skills section
        skills_section_match = re.search(r'(?:SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES)[:\s]*\n+(.+?)(?=\n\n|\n[A-Z]+|\Z)', 
                                         text, re.IGNORECASE | re.DOTALL)
                                         
        if skills_section_match:
            skills_text = skills_section_match.group(1)
            
            # Extract skills by pattern
            skill_patterns = [
                r'(?:^|\n|\•|\-|\*)\s*([\w\s\-\/\&\+\#\.]+?)(?:,|\n|\•|\-|\*|$)',  # Skills separated by commas or bullets
                r'(?:^|\n)([A-Za-z\s\-\/\&\+\#\.]{3,40})(?:\n|$)'  # Skills on their own line
            ]
            
            for pattern in skill_patterns:
                found_skills = re.findall(pattern, skills_text)
                skills.extend([s.strip() for s in found_skills if len(s.strip()) > 0])
                
        # If no skills found in dedicated section, extract from throughout the document
        if not skills:
            # Common skill keywords
            skill_keywords = [
                "proficient in", "experience with", "knowledge of", "skilled in",
                "expertise in", "familiar with", "certified in"
            ]
            
            for keyword in skill_keywords:
                skill_phrases = re.findall(f"{keyword} ([\w\s\-\/\&\+\#\.]+?)(?:\.|\,|\;|\n)", text, re.IGNORECASE)
                skills.extend([s.strip() for s in skill_phrases if len(s.strip()) > 0])
                
        # Remove duplicates and empty strings
        unique_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill and len(skill) > 2 and skill not in unique_skills:
                unique_skills.append(skill)
                
        # Limit to top 10 skills
        return unique_skills[:10] if unique_skills else ["No specific skills extracted"]
        
    def _extract_work_experience(self, text):
        """Extract work experience entries"""
        work_experience = []
        
        # Find the experience section
        experience_section_match = re.search(
            r'(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|PROFESSIONAL EXPERIENCE)[:\s]*\n+(.+?)(?=\n\n\s*(?:EDUCATION|SKILLS|PROJECTS|CERTIFICATIONS)|\Z)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if not experience_section_match:
            return []
            
        experience_text = experience_section_match.group(1)
        
        # Extract job entries - looking for title/company patterns
        # This is simplified - a production parser would need more sophisticated logic
        job_entries = re.split(r'\n\s*\n', experience_text)
        
        for entry in job_entries:
            if not entry.strip():
                continue
                
            job = {
                "title": None,
                "company": None,
                "location": None,
                "dates": None,
                "description": []
            }
            
            # Extract title and company
            title_company_match = re.search(r'(?:^|\n)([^,|]+)(?:,|\||at|\-|–)\s*([^,|\n]+)', entry, re.IGNORECASE)
            if title_company_match:
                job["title"] = title_company_match.group(1).strip()
                job["company"] = title_company_match.group(2).strip()
                
            # Extract dates
            date_pattern = r'(?:^|\s|\()((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\'\-\.]+\d{4}\s*(?:–|-|to)\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\'\-\.]+\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\'\-\.]+\d{4}\s*(?:–|-|to)\s*(?:Present|Current|Now)|(?:\d{1,2}/\d{1,2}/\d{2,4})\s*(?:–|-|to)\s*(?:\d{1,2}/\d{1,2}/\d{2,4}|\s*(?:Present|Current|Now))|\d{4}\s*(?:–|-|to)\s*\d{4}|\d{4}\s*(?:–|-|to)\s*(?:Present|Current|Now))(?:$|\s|\))'
            date_match = re.search(date_pattern, entry, re.IGNORECASE)
            if date_match:
                job["dates"] = date_match.group(1).strip()
                
            # Extract location
            location_match = re.search(r'(?:^|\n)(?:[^,])+,\s*([^,\n]+?)(?:,|\n|$)', entry)
            if location_match:
                potential_location = location_match.group(1).strip()
                # Verify it's not a date or other non-location
                if not re.search(r'\d{4}', potential_location):
                    job["location"] = potential_location
                    
            # Extract bullet points
            lines = entry.split('\n')
            description_lines = []
            for line in lines[1:]:  # Skip the first line which likely has title/company
                line = line.strip()
                if line and not any(x in line for x in [job["title"], job["company"], job["dates"]]):
                    # Remove bullet prefixes
                    line = re.sub(r'^[\•\-\*\>\◦\‣\⁃]+\s*', '', line)
                    if line:
                        description_lines.append(line)
                        
            # Group bullet points if they seem to be split across lines
            if description_lines:
                job["description"] = description_lines
                
            # Only add jobs with at least a title and company
            if job["title"] and job["company"]:
                work_experience.append(job)
                
        return work_experience
        
    def _extract_projects(self, text):
        """Extract project information"""
        projects = []
        
        # Find the projects section
        projects_section_match = re.search(
            r'(?:PROJECTS|PERSONAL PROJECTS|ACADEMIC PROJECTS)[:\s]*\n+(.+?)(?=\n\n\s*(?:EDUCATION|SKILLS|EXPERIENCE|CERTIFICATIONS)|\Z)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if not projects_section_match:
            return []
            
        projects_text = projects_section_match.group(1)
        
        # Extract project entries
        project_entries = re.split(r'\n\s*\n', projects_text)
        
        for entry in project_entries:
            if not entry.strip():
                continue
                
            project = {
                "name": None,
                "dates": None,
                "description": "",
                "details": []
            }
            
            # Extract project name
            lines = entry.split('\n')
            if lines:
                project["name"] = lines[0].strip()
                # Remove bullet prefixes or project prefixes
                project["name"] = re.sub(r'^[\•\-\*\>\◦\‣\⁃]+\s*', '', project["name"])
                project["name"] = re.sub(r'^Project\s*[:-]?\s*', '', project["name"], flags=re.IGNORECASE)
                
                # Extract dates if in the project name line
                date_match = re.search(r'\((.+?)\)|\[(.*?)\]', project["name"])
                if date_match:
                    dates = date_match.group(1) or date_match.group(2)
                    project["dates"] = dates
                    # Remove the dates from the name
                    project["name"] = re.sub(r'\(.+?\)|\[.*?\]', '', project["name"]).strip()
                    
            # Extract description and details
            if len(lines) > 1:
                description_lines = []
                detail_lines = []
                
                for line in lines[1:]:
                    line = line.strip()
                    if line:
                        # Check if it's a bullet point
                        if re.match(r'^[\•\-\*\>\◦\‣\⁃]', line):
                            # Remove the bullet prefix
                            clean_line = re.sub(r'^[\•\-\*\>\◦\‣\⁃]+\s*', '', line)
                            detail_lines.append(clean_line)
                        else:
                            description_lines.append(line)
                            
                if description_lines:
                    project["description"] = " ".join(description_lines)
                if detail_lines:
                    project["details"] = detail_lines
                    
            # Only add projects with a name
            if project["name"]:
                # If no dates were found, add a placeholder
                if not project["dates"]:
                    project["dates"] = "No date specified"
                projects.append(project)
                
        return projects
        
    def save_profile(self, profile_data, output_path=None):
        """Save the parsed profile as JSON"""
        if not profile_data:
            logger.error("No profile data to save")
            return False
            
        if not output_path:
            output_path = 'candidate_profile.json'
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
            logger.info(f"Profile saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving profile to {output_path}: {e}")
            return False

# For testing
if __name__ == "__main__":
    parser = ResumeParser()
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        profile = parser.parse(file_path)
        if profile:
            parser.save_profile(profile)
            print(f"Parsed and saved profile from {file_path}")
        else:
            print(f"Failed to parse {file_path}")
    else:
        print("Please provide a resume file path as an argument")