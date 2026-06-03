"""
ATS Analyzer - Evaluates resume against 10 ATS compatibility criteria
"""
import re
import logging
from typing import List, Dict, Any, Optional
from app.core.analysis.schemas import ATSResult, ATSCriterionScore, ATSGap
from app.core.analysis.tech_tier import get_category_for_skill

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# ATS CRITERIA DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

ATS_CRITERIA = {
    "file_format": {
        "name": "File Format",
        "weight": 10,
        "description": "Resume must be in ATS-compatible format",
        "pass_extensions": [".pdf", ".docx"],
    },
    "design_complexity": {
        "name": "Design Complexity",
        "weight": 15,
        "description": "Avoid tables, text boxes, columns, graphics",
        "fail_indicators": ["table_detected", "text_box", "multi_column", "graphic"],
    },
    "font_standards": {
        "name": "Font Standards",
        "weight": 10,
        "description": "Use standard fonts: Arial, Calibri, Times New Roman",
        "allowed_fonts": ["arial", "calibri", "times new roman", "times", "verdana", "tahoma", "georgia"],
        "min_size": 10,
        "max_size": 12,
    },
    "section_headings": {
        "name": "Section Headings",
        "weight": 10,
        "description": "Use standard section heading names",
        "standard_headings": [
            "work experience", "experience", "employment", "professional experience",
            "education", "academic", "qualification", "qualifications",
            "skills", "technical skills", "technical", "core competencies",
            "projects", "project", "project experience",
            "summary", "profile", "objective", "professional summary",
            "certifications", "certificates", "licenses",
            "achievements", "accomplishments", "awards",
            "publications", "papers", "research",
            "languages", "language proficiency",
            "interests", "hobbies",
        ],
    },
    "contact_info": {
        "name": "Contact Information",
        "weight": 10,
        "description": "Complete contact information present",
        "required": ["email"],
        "preferred": ["phone", "location", "linkedin"],
    },
    "keyword_density": {
        "name": "Keyword Density",
        "weight": 15,
        "description": "Role-relevant keywords present",
        "min_unique_keywords": 5,
    },
    "date_formatting": {
        "name": "Date Formatting",
        "weight": 10,
        "description": "Consistent, parsable date formats",
        "valid_patterns": [
            r"\b(20|19)\d{2}\b",  # YYYY
            r"\b(20|19)\d{2}\s*[-–]\s*(20|19)\d{2}\b",  # YYYY-YYYY
            r"\b(20|19)\d{2}\s*[-–]\s*present\b",  # YYYY-Present
            r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(20|19)\d{2}\b",  # Jan 2020
            r"\b(20|19)\d{2}/(0[1-9]|1[0-2])\b",  # YYYY/MM
        ],
    },
    "bullet_structure": {
        "name": "Bullet Structure",
        "weight": 10,
        "description": "Action verbs + quantified achievements",
        "action_verbs": [
            "developed", "built", "created", "designed", "implemented",
            "managed", "led", "coordinated", "organized",
            "analyzed", "investigated", "researched",
            "optimized", "improved", "enhanced", "increased",
            "reduced", "decreased", "saved",
            "automated", "streamlined", "simplified",
            "delivered", "launched", "released",
            "collaborated", "worked", "partnered",
            "mentored", "trained", "coached",
            "presented", "communicated", "negotiated",
            "resolved", "troubleshot", "debugged",
            "deployed", "configured", "maintained",
            "authored", "documented", "wrote",
        ],
    },
    "length_whitespace": {
        "name": "Length & Whitespace",
        "weight": 5,
        "description": "Appropriate density for experience level",
        "min_words": 200,
        "max_words": 1500,
    },
    "section_completeness": {
        "name": "Section Completeness",
        "weight": 5,
        "description": "Critical sections present",
        "critical_sections": ["education", "experience", "skills"],
    },
}


class ATSAnalyzer:
    """ATS Compatibility Analyzer"""

    def __init__(self):
        self.criteria = ATS_CRITERIA

    async def analyze(
        self,
        raw_text: str,
        file_type: str,
        sections: Optional[Dict[str, str]] = None,
        content_blocks: Optional[List[Dict]] = None,
    ) -> ATSResult:
        """
        Run full ATS analysis on resume content

        Args:
            raw_text: Full extracted text
            file_type: File format (pdf, docx)
            sections: Dict of section_label -> content
            content_blocks: List of content blocks with metadata

        Returns:
            ATSResult with score and detailed breakdown
        """
        sections = sections or {}
        content_blocks = content_blocks or []

        criteria_scores = []
        all_gaps = []

        # 1. File Format Check
        score, details = self._check_file_format(file_type)
        criteria_scores.append(ATSCriterionScore(
            name="File Format",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="File Format",
                severity="critical",
                description=details,
                recommendation="Save your resume as a PDF file"
            ))

        # 2. Design Complexity
        score, details = self._check_design_complexity(content_blocks, raw_text)
        criteria_scores.append(ATSCriterionScore(
            name="Design Complexity",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Design Complexity",
                severity="major",
                description=details,
                recommendation="Remove tables, text boxes, and multi-column layouts"
            ))

        # 3. Font Standards
        score, details = self._check_font_standards(content_blocks)
        criteria_scores.append(ATSCriterionScore(
            name="Font Standards",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Font Standards",
                severity="major",
                description=details,
                recommendation="Use standard fonts like Arial, Calibri, or Times New Roman"
            ))

        # 4. Section Headings
        score, details = self._check_section_headings(sections)
        criteria_scores.append(ATSCriterionScore(
            name="Section Headings",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Section Headings",
                severity="major",
                description=details,
                recommendation="Use standard section heading names"
            ))

        # 5. Contact Information
        score, details = self._check_contact_info(raw_text)
        criteria_scores.append(ATSCriterionScore(
            name="Contact Information",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Contact Information",
                severity="critical",
                description=details,
                recommendation=f"Provide the missing contact details: {details.replace('Missing: ', '')}"
            ))

        # 6. Keyword Density
        score, details = self._check_keyword_density(raw_text, sections)
        criteria_scores.append(ATSCriterionScore(
            name="Keyword Density",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Keyword Density",
                severity="major",
                description=details,
                recommendation="Add more technical keywords relevant to your target role"
            ))

        # 7. Date Formatting
        score, details = self._check_date_formatting(raw_text)
        criteria_scores.append(ATSCriterionScore(
            name="Date Formatting",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Date Formatting",
                severity="minor",
                description=details,
                recommendation="Use consistent date formats like 'Jan 2020 - Present'"
            ))

        # 8. Bullet Structure
        score, details = self._check_bullet_structure(raw_text)
        criteria_scores.append(ATSCriterionScore(
            name="Bullet Structure",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Bullet Structure",
                severity="major",
                description=details,
                recommendation="Use action verbs and quantify achievements"
            ))

        # 9. Length & Whitespace
        score, details = self._check_length_whitespace(raw_text)
        criteria_scores.append(ATSCriterionScore(
            name="Length & Whitespace",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Length & Whitespace",
                severity="minor",
                description=details,
                recommendation="Adjust resume length to 1-2 pages"
            ))

        # 10. Section Completeness
        score, details = self._check_section_completeness(sections)
        criteria_scores.append(ATSCriterionScore(
            name="Section Completeness",
            score=score,
            passed=score >= 70,
            details=details
        ))
        if score < 70:
            all_gaps.append(ATSGap(
                criterion="Section Completeness",
                severity="critical",
                description=details,
                recommendation="Add missing critical sections"
            ))

        # Calculate overall weighted score
        overall_score = self._calculate_weighted_score(criteria_scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(all_gaps)

        return ATSResult(
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            gaps=all_gaps,
            recommendations=recommendations
        )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Individual Criterion Checks
    # ═══════════════════════════════════════════════════════════════════════════════

    def _check_file_format(self, file_type: str) -> tuple:
        """Check if file format is ATS-compatible"""
        if file_type.lower() in [".pdf", "pdf", "docx"]:
            return 100, "PDF format is ATS-compatible"
        return 0, f"File type '{file_type}' is not ATS-compatible. Use PDF."

    def _check_design_complexity(self, content_blocks: List[Dict], raw_text: str) -> tuple:
        """Check for design elements that break ATS"""
        issues = []

        # Check for table indicators in text (common OCR results)
        if "table" in raw_text.lower() and ("row" in raw_text.lower() or "cell" in raw_text.lower()):
            issues.append("possible_table")

        # Check content blocks for column detection
        if content_blocks:
            # Check for unusual reading order that might indicate columns
            x_coords = []
            for block in content_blocks:
                if hasattr(block, '_bbox') and block._bbox:
                    bbox = block._bbox
                    x = getattr(bbox, "l", getattr(bbox, "x", getattr(bbox, "x0", 0))) if not isinstance(bbox, dict) else bbox.get("l", bbox.get("x", bbox.get("x0", 0)))
                    x_coords.append(x)

            if len(set(x_coords)) > 2:  # Multiple column positions
                issues.append("multi_column")

        # Check for common table patterns
        table_patterns = [
            r'\|\s*[-−]+\s*\|',  # |---| table separator
            r'\|\s*\w+\s*\|\s*\w+\s*\|\s*\w+\s*\|',  # Simple table
        ]
        for pattern in table_patterns:
            if re.search(pattern, raw_text):
                issues.append("table_detected")

        if issues:
            return 40, f"Design issues detected: {', '.join(issues)}"
        return 100, "Clean, ATS-friendly layout"

    def _check_font_standards(self, content_blocks: List[Dict]) -> tuple:
        """Check if fonts are standard and readable"""
        if not content_blocks:
            return 70, "Could not verify fonts (no metadata available)"

        # Check extracted font info
        detected_fonts = set()
        for block in content_blocks:
            if hasattr(block, 'font_family'):
                detected_fonts.add(block.font_family.lower())

        allowed = set(self.criteria["font_standards"]["allowed_fonts"])
        non_standard = detected_fonts - allowed

        if non_standard:
            return 60, f"Non-standard fonts detected: {', '.join(non_standard)}"
        return 100, "Standard fonts detected"

    def _check_section_headings(self, sections: Dict[str, str]) -> tuple:
        """Verify section headings are standard"""
        if not sections:
            return 50, "Could not detect sections"

        standard = set(self.criteria["section_headings"]["standard_headings"])
        found_sections = set(sections.keys())

        # Check how many critical sections are present
        critical_keywords = {
            "education": ["education", "academic", "qualification"],
            "experience": ["experience", "work", "employment"],
            "skills": ["skill", "competency"],
        }

        found_critical = []
        for critical, keywords in critical_keywords.items():
            if any(kw in found_sections for kw in keywords):
                found_critical.append(critical)

        if len(found_critical) >= 3:
            return 100, "All critical sections present with standard headings"
        elif len(found_critical) >= 2:
            return 70, f"Found {len(found_critical)}/3 critical sections"
        return 40, f"Only {len(found_critical)}/3 critical sections found"

    def _check_contact_info(self, raw_text: str) -> tuple:
        """Check for complete contact information"""
        found = []
        missing = []

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, raw_text):
            found.append("email")
        else:
            missing.append("email")

        # Phone (allow country codes and spaces)
        phone_patterns = [
            r'\b\d{10,12}\b',  # 10 to 12 digit numbers
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US format
            r'\+?\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',  # Generic international format
        ]
        if any(re.search(p, raw_text) for p in phone_patterns):
            found.append("phone")
        else:
            missing.append("phone")

        # Location (relax to support international formats like City, State, Country without spaces, or common names)
        location_patterns = [
            r'\b[A-Z][a-zA-Z\s]+,\s*[a-zA-Z\s]+(?:,\s*[a-zA-Z\s]+)?\b',  # City, State, Country or City, State
            r'\b[A-Z][a-z]+\b.*\d{5,6}\b',  # City with ZIP/PIN
            r'\b(?:india|usa|united states|uk|united kingdom|canada|germany|australia|singapore|tamilnadu)\b'  # Common keywords
        ]
        if any(re.search(p, raw_text, re.IGNORECASE) for p in location_patterns):
            found.append("location")
        else:
            missing.append("location")

        # LinkedIn
        if "linkedin.com" in raw_text.lower():
            found.append("linkedin")

        if not missing:
            return 100, "Complete contact information"
        return 60, f"Missing: {', '.join(missing)}"

    def _check_keyword_density(self, raw_text: str, sections: Dict[str, str]) -> tuple:
        """Check for role-relevant keywords"""
        # Extract unique words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', raw_text.lower())

        # Filter out common stop words
        stop_words = {
            "the", "and", "for", "are", "but", "not", "you", "all",
            "can", "had", "her", "was", "one", "our", "out", "day",
            "get", "has", "him", "his", "how", "its", "may", "now",
            "old", "see", "than", "that", "this", "with", "have",
            "from", "they", "will", "would", "there", "their", "what",
            "been", "more", "when", "your", "which", "about", "after",
            "could", "other", "some", "them", "then", "these", "into",
        }
        unique_keywords = set(words) - stop_words

        # Count skill-like keywords
        skill_indicators = [
            "python", "java", "javascript", "react", "node", "sql",
            "machine", "learning", "data", "cloud", "aws", "docker",
            "tensorflow", "pytorch", "database", "api", "web", "app",
            "developer", "engineer", "analyst", "manager", "lead",
            "team", "project", "design", "implement", "build", "create",
        ]

        skill_count = sum(1 for kw in unique_keywords if any(s in kw for s in skill_indicators))

        min_required = self.criteria["keyword_density"]["min_unique_keywords"]
        if skill_count >= min_required:
            return 100, f"Found {skill_count} unique skill keywords"
        elif skill_count >= min_required - 2:
            return 70, f"Found {skill_count}/{min_required} skill keywords"
        return 40, f"Only {skill_count}/{min_required} skill keywords found"

    def _check_date_formatting(self, raw_text: str) -> tuple:
        """Verify consistent date formats"""
        patterns = self.criteria["date_formatting"]["valid_patterns"]

        dates_found = []
        for pattern in patterns:
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            dates_found.extend(matches)

        if not dates_found:
            return 50, "No dates found"

        # Check consistency - count pattern types
        pattern_types = set()
        for date in dates_found:
            for pattern in patterns:
                if re.search(pattern, date if isinstance(date, str) else str(date), re.IGNORECASE):
                    pattern_types.add(pattern)
                    break

        if len(pattern_types) == 1:
            return 100, f"Consistent date format"
        elif len(pattern_types) <= 2:
            return 70, f"Multiple date formats detected"
        return 40, "Inconsistent date formats"

    def _check_bullet_structure(self, raw_text: str) -> tuple:
        """Check for action verbs and quantified achievements"""
        action_verbs = set(self.criteria["bullet_structure"]["action_verbs"])

        # Split into lines
        lines = re.split(r'[\n••]', raw_text)

        bullet_lines = [l.strip() for l in lines if l.strip() and len(l.strip()) > 20]

        if not bullet_lines:
            return 30, "No bullet points found"

        # Count action verbs
        verbs_found = 0
        quantified = 0

        for line in bullet_lines:
            line_lower = line.lower()
            if any(verb in line_lower for verb in action_verbs):
                verbs_found += 1

            # Check for numbers/quantification
            if re.search(r'\d+[%$]', line) or re.search(r'\b\d+\s*(users?|customers?|people|files?|requests?|%)', line):
                quantified += 1

        total = len(bullet_lines)
        action_score = (verbs_found / total) * 100 if total > 0 else 0
        quant_score = (quantified / total) * 100 if total > 0 else 0

        final_score = (action_score * 0.6) + (quant_score * 0.4)

        if final_score >= 70:
            return int(final_score), f"Action verbs: {verbs_found}/{total}, Quantified: {quantified}/{total}"
        return int(final_score), f"Low bullet structure (action: {verbs_found}/{total}, quantified: {quantified}/{total})"

    def _check_length_whitespace(self, raw_text: str) -> tuple:
        """Check resume length"""
        word_count = len(raw_text.split())

        min_words = self.criteria["length_whitespace"]["min_words"]
        max_words = self.criteria["length_whitespace"]["max_words"]

        if min_words <= word_count <= max_words:
            return 100, f"Optimal length ({word_count} words)"
        elif word_count < min_words:
            score = int((word_count / min_words) * 100)
            return score, f"Too short ({word_count} words, recommended: {min_words}-{max_words})"
        else:
            score = int(max(0, 100 - ((word_count - max_words) / 100)))
            return score, f"Too long ({word_count} words, recommended: {min_words}-{max_words})"

    def _check_section_completeness(self, sections: Dict[str, str]) -> tuple:
        """Check for critical sections"""
        critical = set(self.criteria["section_completeness"]["critical_sections"])

        if not sections:
            return 30, "No sections detected"

        section_names = set(sections.keys())

        found = []
        for crit in critical:
            # Check if any section name contains the critical keyword
            for section in section_names:
                if crit in section.lower():
                    found.append(crit)
                    break

        found_unique = list(set(found))

        if len(found_unique) >= 3:
            return 100, "All critical sections present"
        elif len(found_unique) == 2:
            return 70, f"Missing 1 critical section"
        return 40, f"Missing {3 - len(found_unique)} critical sections"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Score Calculation
    # ═══════════════════════════════════════════════════════════════════════════════

    def _calculate_weighted_score(self, criteria_scores: List[ATSCriterionScore]) -> int:
        """Calculate weighted overall score"""
        total_weight = 0
        weighted_sum = 0

        for criterion in criteria_scores:
            weight = self.criteria.get(criterion.name.lower().replace(" ", "_"), {}).get("weight", 10)
            weighted_sum += criterion.score * weight
            total_weight += weight

        return int(weighted_sum / total_weight) if total_weight > 0 else 0

    def _generate_recommendations(self, gaps: List[ATSGap]) -> List[str]:
        """Generate prioritized recommendations from gaps"""
        recommendations = []

        # Sort by severity
        severity_order = {"critical": 0, "major": 1, "minor": 2}
        gaps_sorted = sorted(gaps, key=lambda x: severity_order.get(x.severity, 2))

        for gap in gaps_sorted[:5]:  # Top 5 recommendations
            recommendations.append(gap.recommendation)

        return recommendations


# Singleton instance
ats_analyzer = ATSAnalyzer()