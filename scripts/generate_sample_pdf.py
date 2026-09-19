import fitz # PyMuPDF
from pathlib import Path

def create_sample_pdf():
    doc = fitz.open() # new empty PDF
    
    # Page 1: General Policy
    page1 = doc.new_page()
    text1 = (
        "ACME ENTERPRISE - CORPORATE POLICIES AND SERVICE HANDBOOK\n\n"
        "1. OVERVIEW AND MISSION\n"
        "ACME Enterprise provides world-class cloud infrastructure and autonomous AI toolchains.\n"
        "Our mission is to empower developers with reliable, transparent, and scalable automation.\n\n"
        "2. RETURN AND REFUND POLICY\n"
        "All physical hardware appliances purchased directly from ACME are protected by a 30-day money-back guarantee.\n"
        "To initiate a return, customers must request a Return Merchandise Authorization (RMA) from support.\n"
        "Software subscriptions cancelled within 14 days of billing are eligible for a 100% prorated refund.\n\n"
        "3. DATA PRIVACY AND SECURITY\n"
        "All customer datasets processed through our AI pipelines are strictly encrypted at rest using AES-256\n"
        "and in transit using TLS 1.3. User training data is never used to train global public models without explicit consent."
    )
    page1.insert_text((50, 72), text1, fontsize=11)
    
    # Page 2: Service Level Agreement & Escalation
    page2 = doc.new_page()
    text2 = (
        "4. SERVICE LEVEL AGREEMENTS (SLA)\n"
        "ACME Enterprise guarantees 99.95% uptime for all managed cloud endpoints.\n"
        "Planned maintenance windows occur every second Sunday between 02:00 UTC and 04:00 UTC.\n\n"
        "5. TICKET ESCALATION PROCEDURES\n"
        "- Severity 1 (Critical Outage): Initial response within 15 minutes; hourly status updates until resolution.\n"
        "- Severity 2 (Major Degradation): Initial response within 1 hour; resolution targeted within 8 hours.\n"
        "- Severity 3 (General Inquiry): Initial response within 1 business day.\n\n"
        "6. CONTACT INFORMATION\n"
        "Support Portal: https://support.acme-enterprise.com\n"
        "Emergency Hotline: +1-800-555-ACME (Option 2 for Enterprise Support)"
    )
    page2.insert_text((50, 72), text2, fontsize=11)
    
    output_path = Path(__file__).resolve().parent.parent / "datasets" / "company_manual.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    doc.close()
    print(f"Generated sample PDF at: {output_path}")

if __name__ == "__main__":
    create_sample_pdf()
