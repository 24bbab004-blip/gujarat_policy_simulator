from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
def build_report(inp, result, efficiency, risk):
    buf = BytesIO(); doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36,leftMargin=36)
    styles = getSampleStyleSheet(); story = [Paragraph("Gujarat Policy Simulator", styles['Title']),
      Paragraph("DEMO / DECISION-SUPPORT REPORT — NOT AN OFFICIAL GOVERNMENT FORECAST", styles['Heading3']), Spacer(1, 10),
      Paragraph(f"<b>Policy:</b> {inp['name']} &nbsp;&nbsp; <b>Category:</b> {inp['category']}", styles['BodyText']),
      Paragraph(f"<b>Geography:</b> {', '.join(inp['districts'])}", styles['BodyText']), Spacer(1, 10)]
    f=result['financial']; b=result['beneficiaries']; imp=result['impact']
    rows=[["Metric", "Estimated result"],["Current cost", f"₹{f['current_cost']:,.0f}"],["Proposed cost", f"₹{f['proposed_cost']:,.0f}"],["Additional cost", f"₹{f['additional_cost']:,.0f}"],["Beneficiaries", f"{b['proposed']:,.0f}"],["Estimated impact", f"{imp['score']}/100"],["Efficiency", f"{efficiency['total']}/100"],["Risk score", f"{risk['score']}/100"]]
    table=Table(rows, colWidths=[200,250]); table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0b4f6c')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.25,colors.grey),('PADDING',(0,0),(-1,-1),6)])); story += [table, Spacer(1,10), Paragraph("Assumptions and limitations", styles['Heading2'])]
    for a in result['assumptions']: story.append(Paragraph("• "+a, styles['BodyText']))
    story.append(Spacer(1,8)); story.append(Paragraph("Simulation results are estimates generated from available data and assumptions. They are intended to support policy analysis and should not be treated as official government forecasts or decisions.", styles['BodyText']))
    doc.build(story); return buf.getvalue()
