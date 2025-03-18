# =============================================================================
# ENHANCED PDF GENERATION WITH DETAILED TABLES
# =============================================================================
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import datetime

def create_enhanced_pdf_report(client_name, province, calculation_details, present_value_details, 
                             result, collateral_benefits, missed_time_unit, missed_time, output_path, 
                             birthdate=None, retirement_age=None):
    """
    Create a professionally-styled PDF report with comprehensive details organized in distinct sections.
    
    Args:
        client_name: Name of the client
        province: Client's province for taxation purposes
        calculation_details: Dictionary containing past lost wages calculation details
        present_value_details: Dictionary containing future lost wages calculation details
        result: Dictionary containing income and deduction details
        collateral_benefits: Dictionary containing collateral benefit details
        missed_time_unit: Unit of missed time (days, weeks, months, etc.)
        missed_time: Amount of missed time
        output_path: Path where the PDF will be saved
        birthdate: Client's date of birth (optional)
        retirement_age: Client's retirement age (optional)
    
    Returns:
        Path to the created PDF file
    """
    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=letter, 
                          leftMargin=0.5*inch, rightMargin=0.5*inch,
                          topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#2d5ca9'),
        spaceAfter=0.2*inch,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#2d5ca9'),
        spaceAfter=0.15*inch,
        spaceBefore=0.2*inch,
        borderWidth=0,
        borderPadding=0,
        borderColor=None,
        borderRadius=None
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitleStyle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2d5ca9'),
        spaceBefore=0.15*inch,
        spaceAfter=0.1*inch,
        underline=True
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=0.05*inch,
        spaceAfter=0.05*inch
    )
    
    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica-Bold'
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    
    # Start building document
    elements = []
    
    # Title
    elements.append(Paragraph(f"PAST AND FUTURE WAGE LOSS", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Client name
    elements.append(Paragraph(f"{client_name}", subtitle_style))
    
    # Date
    today = datetime.date.today().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Prepared: {today}", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # 1. ASSUMPTIONS SECTION
    elements.append(Paragraph("Assumptions", section_title_style))
    
    # Get formatted province name
    if province.lower() == "nova scotia":
        province_display = "Nova Scotia"
    elif province.lower() == "new brunswick":
        province_display = "New Brunswick" 
    elif province.lower() == "prince edward island":
        province_display = "Prince Edward Island"
    elif province.lower() == "newfoundland" or province.lower() == "newfoundland and labrador":
        province_display = "Newfoundland and Labrador"
    else:
        province_display = province.capitalize()
    
    # Jurisdiction information
    jurisdiction_data = [
        [Paragraph("Parameter", table_header_style), Paragraph("Value", table_header_style)],
        ["Applicable Law:", province_display],
        ["Applicable Tax Rates:", province_display]
    ]
    
    jurisdiction_table = Table(jurisdiction_data, colWidths=[2.5*inch, 4*inch])
    jurisdiction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#e6eef7')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#2d5ca9')),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
	('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(jurisdiction_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Income and deductions information - Filter out zero values except for specific cases
    income_data = [
        [Paragraph("Income & Deductions", table_header_style), Paragraph("Amount", table_header_style)],
        ["Gross Salary:", f"${result.get('Gross Income', 0):,.2f}"]
    ]
    
    # For PEI, add a special note about calculations being based on gross salary
    if province.lower() == "prince edward island":
        income_data.append(["Note:", "In Prince Edward Island, past and future lost wages are calculated using gross salary, not net."])
    else:
        # For other provinces, add non-zero deductions
        if result.get('Federal Tax', 0) > 0:
            income_data.append(["Federal Tax:", f"${result.get('Federal Tax', 0):,.2f}"])
        
        if result.get(f'{province.capitalize()} Tax', 0) > 0:
            income_data.append([f"{province_display} Tax:", f"${result.get(f'{province.capitalize()} Tax', 0):,.2f}"])
        
        if result.get('CPP Contribution', 0) > 0:
            income_data.append(["CPP Contribution:", f"${result.get('CPP Contribution', 0):,.2f}"])
        
        if result.get('CPP2 Contribution', 0) > 0:
            income_data.append(["CPP2 Contribution:", f"${result.get('CPP2 Contribution', 0):,.2f}"])
        
        if result.get('EI Contribution', 0) > 0:
            income_data.append(["EI Contribution:", f"${result.get('EI Contribution', 0):,.2f}"])
        
        if result.get('Total Deductions', 0) > 0:
            income_data.append(["Total Deductions:", f"${result.get('Total Deductions', 0):,.2f}"])
    
    # Always include net pay
    income_data.append(["Net of Taxes:", f"${result.get('Net Pay (Provincially specific deductions for damages)', 0):,.2f}"])
    
    income_table = Table(income_data, colWidths=[2.5*inch, 4*inch])
    
    # Determine last row index for styling
    last_row_index = len(income_data) - 1
    
    income_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#e6eef7')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#2d5ca9')),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Highlight Net Pay row (last row)
        ('BACKGROUND', (0, last_row_index), (1, last_row_index), colors.HexColor('#e6eef7')),
        ('FONTNAME', (0, last_row_index), (1, last_row_index), 'Helvetica-Bold'),
	('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(income_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Add explanation of collateral benefits
    elements.append(Paragraph("Collateral benefits are amounts received from other sources that may offset the economic damages. These benefits are subtracted from the calculated losses to avoid double recovery.", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Collateral benefits information - only include non-zero benefits
    benefits_data = [
        [Paragraph("Collateral Benefits", table_header_style), 
         Paragraph("Annual Amount", table_header_style), 
         Paragraph("Description", table_header_style)]
    ]
    
    # Filter and add only non-zero benefits with descriptions
    benefit_descriptions = {
        "EI Benefits": "Employment Insurance sickness benefits (limited to 26 weeks)",
        "Section B Benefits": "No-fault automobile insurance benefits",
        "LTD Benefits": "Long-term disability benefits from employer or private insurance",
        "CPPD Benefits": "Canada Pension Plan disability benefits",
        "Other Benefits": "Additional benefits from other sources"
    }
    
    has_benefits = False
    
    if collateral_benefits.get('EI Benefits (annual)', 0) > 0:
        benefits_data.append(["EI Benefits:", 
                             f"${collateral_benefits.get('EI Benefits (annual)', 0):,.2f}",
                             benefit_descriptions["EI Benefits"]])
        has_benefits = True
        
    if collateral_benefits.get('Section B Benefits (annual)', 0) > 0:
        benefits_data.append(["Section B Benefits:", 
                             f"${collateral_benefits.get('Section B Benefits (annual)', 0):,.2f}",
                             benefit_descriptions["Section B Benefits"]])
        has_benefits = True
        
    if collateral_benefits.get('LTD Benefits (annual)', 0) > 0:
        benefits_data.append(["LTD Benefits:", 
                             f"${collateral_benefits.get('LTD Benefits (annual)', 0):,.2f}",
                             benefit_descriptions["LTD Benefits"]])
        has_benefits = True
        
    if collateral_benefits.get('CPPD Benefits (annual)', 0) > 0:
        benefits_data.append(["CPPD Benefits:", 
                             f"${collateral_benefits.get('CPPD Benefits (annual)', 0):,.2f}",
                             benefit_descriptions["CPPD Benefits"]])
        has_benefits = True
        
    if collateral_benefits.get('Other Benefits (annual)', 0) > 0:
        benefits_data.append(["Other Benefits:", 
                             f"${collateral_benefits.get('Other Benefits (annual)', 0):,.2f}",
                             benefit_descriptions["Other Benefits"]])
        has_benefits = True
    
    # Add New Brunswick specific note if applicable
    if province.lower() == "new brunswick":
        benefits_data.append(["Note:", "", 
                             "In New Brunswick, LTD and CPPD benefits are not deducted from future lost wage calculations."])
    
    # Only add total if there are benefits
    if has_benefits:
        benefits_data.append(["Total Collateral Benefits:", 
                             f"${collateral_benefits.get('Total Annual Future Benefits', 0):,.2f}",
                             "Sum of all annual collateral benefits"])
    else:
        benefits_data.append(["No Collateral Benefits", "$0.00", "No offsetting benefits are being received"])
    
    # Adjust column widths for the description
    benefits_table = Table(benefits_data, colWidths=[1.5*inch, 1.5*inch, 3.5*inch])
    
    # Determine the last row index for styling
    benefits_last_row = len(benefits_data) - 1
    
    benefits_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#e6eef7')),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.HexColor('#2d5ca9')),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 9),
        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Highlight Total Benefits row
        ('BACKGROUND', (0, benefits_last_row), (2, benefits_last_row), colors.HexColor('#e6eef7')),
        ('FONTNAME', (0, benefits_last_row), (2, benefits_last_row), 'Helvetica-Bold'),
	('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(benefits_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Personal information
    personal_data = [
        [Paragraph("Personal Information", table_header_style), Paragraph("Details", table_header_style)],
        ["Date of Birth:", birthdate.strftime("%Y-%m-%d") if birthdate else "Not specified"],
        ["Retirement Age:", str(retirement_age) if retirement_age else "Not specified"],
        ["Time Missed:", f"{missed_time} {missed_time_unit}"],
        ["Discount Rate:", f"{present_value_details.get('discount_rate', 0)*100:.2f}%"],
        ["Prejudgment Interest:", f"{calculation_details.get('PJI Rate', 0):.2f}%"]
    ]
    
    personal_table = Table(personal_data, colWidths=[2.5*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#e6eef7')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#2d5ca9')),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
	('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(personal_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 2. PAST WAGE LOSS SECTION
    elements.append(Paragraph("Past Wage Loss", section_title_style))
    
    # Get gross lost wages
    if missed_time_unit.lower() == "days":
        gross_daily_wage = result.get('Gross Income', 0) / (result.get('Working Days', 252) or 252)
        gross_lost_wages = gross_daily_wage * float(missed_time)
    elif missed_time_unit.lower() == "weeks":
        gross_weekly_wage = result.get('Gross Income', 0) / 52
        gross_lost_wages = gross_weekly_wage * float(missed_time)
    elif missed_time_unit.lower() == "months":
        gross_monthly_wage = result.get('Gross Income', 0) / 12
        gross_lost_wages = gross_monthly_wage * float(missed_time)
    else:
        gross_lost_wages = result.get('Gross Income', 0) * float(missed_time)
    
    # Calculate collateral benefits deduction for past period
    past_collateral_benefits = collateral_benefits.get('Total Past Benefits', 0)
    
    past_data = [
        [Paragraph("Item", table_header_style), Paragraph("Amount", table_header_style)],
        ["Gross Lost Income:", f"${gross_lost_wages:,.2f}"],
        ["Net Lost Income:", f"${calculation_details.get('Original Past Lost Wages', 0) + past_collateral_benefits:,.2f}"],
        ["Prejudgment Interest:", f"${calculation_details.get('Interest Amount', 0):,.2f}"],
        ["Collateral Benefits Deduction:", f"-${past_collateral_benefits:,.2f}"],
        ["Total Past Lost Wages:", f"${calculation_details.get('Past Lost Wages with Interest', 0):,.2f}"]
    ]
    
    past_table = Table(past_data, colWidths=[3.25*inch, 3.25*inch])
    past_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#e6eef7')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#2d5ca9')),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Highlight Total Past Lost Wages row
        ('BACKGROUND', (0, 5), (1, 5), colors.HexColor('#e6eef7')),
        ('FONTNAME', (0, 5), (1, 5), 'Helvetica-Bold'),
	('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(past_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 3. FUTURE WAGE LOSS SECTION
    elements.append(Paragraph("Future Wage Loss", section_title_style))
    
    # Add explanation of future wage loss calculation
    future_wage_explanation = (
        "Future wage loss represents the present value of income expected to be lost from today until the end of the loss period. "
        "This calculation uses the annual net income, applies appropriate discounting to account for the time value of money, "
        "and deducts ongoing collateral benefits."
    )
    elements.append(Paragraph(future_wage_explanation, normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # If we have retirement information, add context about the loss period
    if retirement_age and birthdate:
        current_age = (datetime.date.today() - birthdate).days / 365.25
        elements.append(Paragraph(
            f"Loss period is calculated from present day until retirement at age {retirement_age} "
            f"(current age: {current_age:.1f} years).", normal_style
        ))
        elements.append(Spacer(1, 0.1*inch))
    
    # Calculate annual collateral benefits
    annual_collateral_benefits = collateral_benefits.get('Total Annual Future Benefits', 0)
    
    future_data = [
        [Paragraph("Item", table_header_style), Paragraph("Amount", table_header_style), Paragraph("Explanation", table_header_style)],
        ["Annual Gross Income:", f"${result.get('Gross Income', 0):,.2f}", "Projected annual salary"]
    ]
    
    # Add collateral benefits if applicable
    if annual_collateral_benefits > 0:
        future_data.append([
            "Annual Collateral Benefits:", 
            f"-${annual_collateral_benefits:,.2f}", 
            "Ongoing benefits that offset wage loss"
        ])
    
    future_data.append([
        "Net Annual Income:", 
        f"${present_value_details.get('annual_salary', 0):,.2f}", 
        "Gross income minus collateral benefits"
    ])
    
    future_data.append([
        "Loss Period:", 
        f"{present_value_details.get('time_horizon', 0):.2f} years", 
        "Duration of expected future losses"
    ])
    
    future_data.append([
        "Discount Rate:", 
        f"{present_value_details.get('discount_rate', 0)*100:.2f}%", 
        "Rate used to calculate present value of future losses"
    ])
    
    future_data.append([
        "Total Future Lost Wages:", 
        f"${present_value_details.get('present_value', 0):,.2f}", 
        "Present value of future income stream"
    ])
    
    # Adjust column widths for the description
    future_table = Table(future_data, colWidths=[2*inch, 1.5*inch, 3*inch])
    
    # Get the last row index for styling
    future_last_row = len(future_data) - 1
    
    future_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#e6eef7')),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.HexColor('#2d5ca9')),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 9),
        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Highlight Total Future Lost Wages row
        ('BACKGROUND', (0, future_last_row), (2, future_last_row), colors.HexColor('#e6eef7')),
        ('FONTNAME', (0, future_last_row), (2, future_last_row), 'Helvetica-Bold'),
	('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(future_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # 4. TOTAL ECONOMIC DAMAGES SECTION
    elements.append(Paragraph("Total Wage Loss", section_title_style))
    
    # Add explanation of total economic damages
    total_explanation = (
        "The total economic damages represent the sum of past and future wage losses. "
        "This is the total compensation required to address the economic impact of lost income."
    )
    elements.append(Paragraph(total_explanation, normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Calculate totals
    past_lost_wages = calculation_details.get('Past Lost Wages with Interest', 0)
    future_lost_wages = present_value_details.get('present_value', 0)
    total_damages = past_lost_wages + future_lost_wages
    
    total_data = [
        [Paragraph("Item", table_header_style), Paragraph("Amount", table_header_style), Paragraph("Source", table_header_style)],
        ["Past Lost Wages:", f"${past_lost_wages:,.2f}", "From past wage loss calculation including interest"],
        ["Future Lost Wages:", f"${future_lost_wages:,.2f}", "Present value of future losses"],
        ["TOTAL ECONOMIC DAMAGES:", f"${total_damages:,.2f}", "Sum of past and future losses"]
    ]
    
    # Adjust column widths for the description
    total_table = Table(total_data, colWidths=[2*inch, 1.5*inch, 3*inch])
    
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#e6eef7')),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.HexColor('#2d5ca9')),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 9),
        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        # Highlight Total row with special background
        ('BACKGROUND', (0, 3), (2, 3), colors.HexColor('#2d5ca9')),
        ('TEXTCOLOR', (0, 3), (2, 3), colors.white),
        ('FONTNAME', (0, 3), (2, 3), 'Helvetica-Bold'),
	('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elements.append(total_table)
    
    # Add methodology section
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Methodology & Notes", section_title_style))
    
    methodology_text = [
        "• Past losses are calculated based on the actual time missed from work, using the appropriate rate of pay.",
        "• Future losses are calculated using the present value of an income stream, discounted at the specified rate.",
        "• Prejudgment interest is calculated from the midpoint of the loss period to the present date.",
        "• Collateral benefits are deducted to avoid double recovery of compensation.",
    ]
    
    # Add PEI-specific methodology note if applicable
    if province.lower() == "prince edward island":
        methodology_text.append("• In Prince Edward Island, damages are based on gross income rather than net income as per provincial law.")
    
    # Add New Brunswick-specific methodology note if applicable
    if province.lower() == "new brunswick":
        methodology_text.append("• In New Brunswick, LTD and CPPD benefits are not deducted from future lost wages as per provincial law.")
    
    for line in methodology_text:
        elements.append(Paragraph(line, normal_style))
    
    # Add footer with disclaimer
    elements.append(Spacer(1, 0.3*inch))
    footer_text = "This report is for informational purposes only and should be reviewed by a qualified professional. "\
                 "The calculations are based on the assumptions provided and may not reflect all applicable factors."
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build the document
    doc.build(elements)
    
    return output_path

# For testing and standalone use
if __name__ == "__main__":
    # Example usage with sample data
    client_name = "John Doe"
    province = "Nova Scotia"
    calculation_details = {
        "Loss Date": "2022-01-01",
        "Current Date": "2023-01-01",
        "Midpoint Date": "2022-07-01",
        "Years Between Midpoint and Current Date": 0.5,
        "Original Past Lost Wages": 50000.00,
        "PJI Rate": 5.0,
        "Interest Amount": 1250.00,
        "Past Lost Wages with Interest": 51250.00
    }
    present_value_details = {
        "annual_salary": 75000.00,
        "monthly_payment": 6250.00,
        "time_horizon": 10.0,
        "total_months": 120,
        "discount_rate": 0.025,
        "present_value": 675000.00,
        "future_collateral_benefits": 0.00
    }
    result = {
        "Gross Income": 100000.00,
        "Federal Tax": 15000.00,
        "Nova Scotia Tax": 10000.00,
        "CPP Contribution": 3500.00,
        "CPP2 Contribution": 500.00,
        "EI Contribution": 1000.00,
        "Total Deductions": 30000.00,
        "Net Pay (Provincially specific deductions for damages)": 70000.00,
        "Daily Net Pay": 277.78,
        "Hourly Net Pay": 34.72,
        "Weekly Net Pay": 1346.15,
        "Monthly Net Pay": 5833.33,
        "Working Days": 252
    }
    collateral_benefits = {
        "EI Benefits (to date)": 5000.00,
        "Section B Benefits (to date)": 2000.00,
        "LTD Benefits (to date)": 0.00,
        "CPPD Benefits (to date)": 0.00,
        "Other Benefits (to date)": 0.00,
        "Total Past Benefits": 7000.00,
        "EI Benefits (annual)": 10000.00,
        "Section B Benefits (annual)": 5000.00,
        "LTD Benefits (annual)": 0.00,
        "CPPD Benefits (annual)": 0.00,
        "Other Benefits (annual)": 0.00,
        "Total Annual Future Benefits": 15000.00
    }
    
    # Sample birthdate and retirement age
    birthdate = datetime.date(1980, 1, 1)
    retirement_age = 65
    
    # Create PDF
    create_enhanced_pdf_report(
        client_name=client_name,
        province=province,
        calculation_details=calculation_details,
        present_value_details=present_value_details,
        result=result,
        collateral_benefits=collateral_benefits,
        missed_time_unit="months",
        missed_time=6,
        output_path="enhanced_economic_damages_report.pdf",
        birthdate=birthdate,
        retirement_age=retirement_age
    )
    
    print("Enhanced PDF report generated successfully!")
