import os
import uuid
from datetime import datetime
from pathlib import Path
from fpdf import FPDF
import matplotlib.pyplot as plt

from app.models.interview import InterviewSession, EvaluationScore

OUTPUTS_DIR = Path("data/outputs")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 15)
        self.cell(0, 10, "AI Interview Evaluation Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_radar_chart(score: EvaluationScore, output_path: str):
    labels = [
        'Answer Quality', 'Technical Correctness', 'Communication',
        'Problem Solving', 'Attitude & Confidence', 'Overall Recommendation'
    ]
    values = [
        score.answer_quality, score.technical_correctness, score.communication,
        score.problem_solving, score.attitude_confidence, score.overall_recommendation
    ]
    
    # Complete the loop
    values += values[:1]
    
    import numpy as np
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='blue', alpha=0.25)
    ax.plot(angles, values, color='blue', linewidth=2)
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=10)
    ax.set_ylim(0, 10)
    
    plt.title("Candidate Profile", size=15, color='black', y=1.1)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def generate_pdf_report(session: InterviewSession) -> str:
    if not session.state.evaluation:
        raise ValueError("Cannot generate report without an evaluation.")
        
    score = session.state.evaluation
    
    pdf = PDFReport()
    pdf.add_page()
    
    # Candidate Info
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Candidate: {session.candidate_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Date: {session.start_time.strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Radar Chart
    chart_path = str(OUTPUTS_DIR / f"{session.room_name}_radar_{uuid.uuid4().hex[:6]}.png")
    generate_radar_chart(score, chart_path)
    pdf.image(chart_path, w=120, x=45)
    pdf.ln(5)
    
    # Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, score.summary)
    pdf.ln(5)
    
    # Detailed Scores
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Detailed Scores (0-10)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    def add_score(label, value, feedback):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 8, label)
        pdf.cell(20, 8, f"{value}/10")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 8, feedback)
        
    add_score("Answer Quality:", score.answer_quality, score.feedback_details.get("answer_quality", ""))
    add_score("Technical Correctness:", score.technical_correctness, score.feedback_details.get("technical_correctness", ""))
    add_score("Communication:", score.communication, score.feedback_details.get("communication", ""))
    add_score("Problem Solving:", score.problem_solving, score.feedback_details.get("problem_solving", ""))
    add_score("Attitude & Confidence:", score.attitude_confidence, score.feedback_details.get("attitude_confidence", ""))
    add_score("Overall Recommendation:", score.overall_recommendation, score.feedback_details.get("overall_recommendation", ""))
    pdf.ln(5)
    
    # Strengths
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Key Strengths", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for s in score.strengths:
        pdf.cell(5, 6, "-")
        pdf.multi_cell(0, 6, s)
    pdf.ln(5)
    
    # Areas for Improvement
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Areas for Improvement", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for a in score.areas_for_improvement:
        pdf.cell(5, 6, "-")
        pdf.multi_cell(0, 6, a)
        
    # Cleanup chart image
    try:
        os.remove(chart_path)
    except Exception:
        pass
        
    report_path = str(OUTPUTS_DIR / f"{session.room_name}_interview_report.pdf")
    pdf.output(report_path)
    return report_path
