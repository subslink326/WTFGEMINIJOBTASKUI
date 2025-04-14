/**
 * Report Formatter - Enhances the job analysis report with visual styling
 */
class ReportFormatter {
    constructor() {
        this.sectionIcons = {
            'job posting': 'fa-briefcase',
            'analyze job posting': 'fa-briefcase',
            'candidate data mapping': 'fa-user-check',
            'ideal profile': 'fa-star',
            'company vetting': 'fa-building',
            'initial company vetting': 'fa-building',
            'deep dive company research': 'fa-search-plus',
            'synthesize findings': 'fa-chart-pie',
            'resume tailoring': 'fa-file-alt',
            'cover letter': 'fa-envelope',
            'responsibilities': 'fa-tasks',
            'qualifications': 'fa-check-circle',
            'keywords': 'fa-key',
            'skills': 'fa-tools',
            'experience': 'fa-history',
            'culture': 'fa-users',
            'company overview': 'fa-info-circle',
            'leadership': 'fa-user-tie',
            'products': 'fa-box',
            'market': 'fa-chart-line',
            'news': 'fa-newspaper',
            'financial': 'fa-dollar-sign',
            'mission': 'fa-bullseye',
            'values': 'fa-heart',
            'social media': 'fa-share-alt',
            'linkedin': 'fa-linkedin',
            'salary': 'fa-money-bill-wave',
            'employee': 'fa-smile',
            'overall fit': 'fa-balance-scale',
            'unique value': 'fa-gem'
        };
        
        this.skillColors = {
            'strong': 'bg-green-100 text-green-800',
            'good': 'bg-blue-100 text-blue-800',
            'moderate': 'bg-yellow-100 text-yellow-800',
            'weak': 'bg-orange-100 text-orange-800',
            'poor': 'bg-red-100 text-red-800',
            'match': 'bg-green-100 text-green-800',
            'partial': 'bg-yellow-100 text-yellow-800',
            'gap': 'bg-red-100 text-red-800'
        };
    }
    
    /**
     * Format the entire report with enhanced visual styling
     */
    formatReport(markdownText) {
        // First convert markdown to HTML using marked
        let htmlContent = marked.parse(markdownText);
        
        // Apply section styling
        htmlContent = this.formatSections(htmlContent);
        
        // Add skill badges
        htmlContent = this.formatSkillBadges(htmlContent);
        
        // Format company info boxes
        htmlContent = this.formatCompanyInfo(htmlContent);
        
        // Format assessment ratings
        htmlContent = this.formatAssessmentRatings(htmlContent);
        
        // Format LinkedIn and social media links
        htmlContent = this.formatSocialLinks(htmlContent);
        
        // Format salary information
        htmlContent = this.formatSalaryInfo(htmlContent);
        
        return htmlContent;
    }
    
    /**
     * Format main sections with icons and styling
     */
    formatSections(html) {
        // Find all h2 and h3 headings and add icons based on content
        for (const [keyword, iconClass] of Object.entries(this.sectionIcons)) {
            const regex = new RegExp(`(<h[23][^>]*>)(.*?\\b${keyword}\\b.*?)(</h[23]>)`, 'gi');
            html = html.replace(regex, (match, openTag, content, closeTag) => {
                return `
                <div class="section-header bg-blue-50 p-4 rounded-lg shadow-md mb-6 mt-8">
                    ${openTag}<i class="fas ${iconClass} mr-2 text-blue-600"></i>${content}${closeTag}
                </div>`;
            });
        }
        
        // Add general styling to any remaining h2, h3 without specific icons
        html = html.replace(/(<h2[^>]*>)(.*?)(<\/h2>)/g, 
            '<div class="section-header bg-blue-50 p-4 rounded-lg shadow-md mb-6 mt-8">$1<i class="fas fa-file-alt mr-2 text-blue-600"></i>$2$3</div>');
        
        html = html.replace(/(<h3[^>]*>)(.*?)(<\/h3>)/g, 
            '<div class="subsection-header bg-gray-50 p-3 rounded-md shadow-sm mb-4 mt-6">$1<i class="fas fa-list-alt mr-2 text-blue-500"></i>$2$3</div>');
        
        return html;
    }
    
    /**
     * Format skill and keyword mentions as badges
     */
    formatSkillBadges(html) {
        // Find skill lists
        html = html.replace(/(?<=<li>)(.*?)(strong match|good match|moderate match|weak match|gap|match|strong|good|moderate|weak|poor)(?:\s+|\b)(.*?)(?=<\/li>)/gi, 
            (match, before, rating, after) => {
                const lowerRating = rating.toLowerCase();
                const colorClass = this.skillColors[lowerRating] || 'bg-gray-100 text-gray-800';
                
                return `${before}<span class="inline-block ${colorClass} rounded-full px-3 py-1 text-sm font-semibold mr-2 mb-2">${rating}</span>${after}`;
            });
        
        // Find keywords and technical terms
        const technicalTerms = [
            'JavaScript', 'Python', 'Java', 'C#', 'C\\+\\+', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'TypeScript',
            'React', 'Angular', 'Vue', 'Node\\.js', 'Express', 'Django', 'Flask', 'Spring', 'Rails',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'GitHub Actions',
            'SQL', 'NoSQL', 'MongoDB', 'MySQL', 'PostgreSQL', 'Oracle', 'Redis',
            'DevOps', 'CI/CD', 'Agile', 'Scrum', 'Kanban', 'Waterfall', 'TDD', 'BDD'
        ];
        
        const pattern = new RegExp(`\\b(${technicalTerms.join('|')})\\b`, 'g');
        html = html.replace(pattern, '<span class="bg-blue-50 text-blue-700 px-1 rounded">$1</span>');
        
        return html;
    }
    
    /**
     * Format company information in attractive boxes
     */
    formatCompanyInfo(html) {
        // Create info boxes for company data
        const companyInfoSections = [
            'Company Overview', 'Products & Services', 'History & Founding', 'Key Leadership',
            'Business Model', 'Market & Competitors', 'Recent News', 'Financial Health',
            'Mission, Vision & Values', 'Culture Insights'
        ];
        
        companyInfoSections.forEach(section => {
            const regex = new RegExp(`(<h[3-4][^>]*>${section}.*?</h[3-4]>)(.*?)(?=<h[3-4]|<h2|$)`, 'is');
            html = html.replace(regex, (match, heading, content) => {
                return `
                <div class="company-info-box border border-blue-200 rounded-lg overflow-hidden mb-8">
                    <div class="bg-blue-100 p-3">
                        ${heading}
                    </div>
                    <div class="p-4 bg-white">
                        ${content}
                    </div>
                </div>`;
            });
        });
        
        return html;
    }
    
    /**
     * Format assessment ratings with visual indicators
     */
    formatAssessmentRatings(html) {
        // Look for assessment text like "Strong Fit" or "Moderate Match"
        const ratingPattern = /\b(Strong|Good|Moderate|Weak|Poor)\s+(Fit|Match|Alignment)\b/gi;
        
        html = html.replace(ratingPattern, (match, rating, type) => {
            const lowerRating = rating.toLowerCase();
            const colorClass = this.skillColors[lowerRating] || 'bg-gray-100 text-gray-800';
            
            // Create a rating badge with stars
            let stars = '';
            if (lowerRating === 'strong') stars = '★★★★★';
            else if (lowerRating === 'good') stars = '★★★★☆';
            else if (lowerRating === 'moderate') stars = '★★★☆☆';
            else if (lowerRating === 'weak') stars = '★★☆☆☆';
            else if (lowerRating === 'poor') stars = '★☆☆☆☆';
            
            return `<div class="inline-flex items-center ${colorClass} rounded-lg px-4 py-2 font-bold text-lg">
                ${rating} ${type} <span class="ml-2">${stars}</span>
            </div>`;
        });
        
        return html;
    }
    
    /**
     * Format social media links
     */
    formatSocialLinks(html) {
        // Look for LinkedIn URLs
        const linkedinPattern = /(https?:\/\/(?:www\.)?linkedin\.com\/(?:company|in)\/[^/\s"]+)/gi;
        
        html = html.replace(linkedinPattern, 
            '<a href="$1" target="_blank" class="inline-flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">' +
            '<i class="fab fa-linkedin mr-2"></i>LinkedIn Profile</a>');
        
        return html;
    }
    
    /**
     * Format salary information
     */
    formatSalaryInfo(html) {
        // Look for salary ranges and comparisons
        const salaryPattern = /\$[0-9,]+ to \$[0-9,]+|\$[0-9,]+ - \$[0-9,]+|\$[0-9,]+ per year/g;
        
        html = html.replace(salaryPattern, match => {
            return `<div class="inline-block bg-green-50 text-green-800 border border-green-200 rounded-lg px-4 py-2 font-semibold">
                <i class="fas fa-money-bill-wave mr-2"></i>${match}
            </div>`;
        });
        
        // Format salary comparisons
        const comparisonPattern = /(above|below|at) market rate/gi;
        html = html.replace(comparisonPattern, (match, position) => {
            let colorClass = 'bg-yellow-50 text-yellow-800 border-yellow-200';
            let icon = 'fa-equals';
            
            if (position.toLowerCase() === 'above') {
                colorClass = 'bg-green-50 text-green-800 border-green-200';
                icon = 'fa-arrow-up';
            } else if (position.toLowerCase() === 'below') {
                colorClass = 'bg-red-50 text-red-800 border-red-200';
                icon = 'fa-arrow-down';
            }
            
            return `<div class="inline-block ${colorClass} border rounded-lg px-4 py-2 font-semibold">
                <i class="fas ${icon} mr-2"></i>${match}
            </div>`;
        });
        
        return html;
    }
}

// Initialize formatter on page load
document.addEventListener('DOMContentLoaded', () => {
    window.reportFormatter = new ReportFormatter();
});