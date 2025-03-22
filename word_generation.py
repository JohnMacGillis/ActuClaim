# =============================================================================
# WORD DOCUMENT GENERATION
# =============================================================================
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import datetime
import re

def create_word_report(client_name, province, calculation_details, present_value_details, 
                     result, collateral_benefits, missed_time_unit, missed_time, output_path, 
                     birthdate=None, retirement_age=None, **kwargs):
    """
    Create a Word document report based on the template, filling in dynamic fields.
    
    Args:
        client_name: Name of the client
        province: Client's province for taxation purposes
        calculation_details: Dictionary containing past lost wages calculation details
        present_value_details: Dictionary containing future lost wages calculation details
        result: Dictionary containing income and deduction details
        collateral_benefits: Dictionary containing collateral benefit details
        missed_time_unit: Unit of missed time (days, weeks, months, etc.)
        missed_time: Amount of missed time
        output_path: Path where the Word document will be saved
        birthdate: Client's date of birth (optional)
        retirement_age: Client's retirement age (optional)
        **kwargs: Additional keyword arguments including:
            - loss_date: Date of loss/accident
            - current_date: Current date
            - ei_days_remaining: Remaining EI days
            - missed_pay: Missed pay amount
            - net_past_lost_wages: Net past lost wages amount
    
    Returns:
        Path to the created Word document file
    """
    # Get optional parameters
    loss_date = kwargs.get('loss_date')
    current_date = kwargs.get('current_date', datetime.date.today())
    ei_days_remaining = kwargs.get('ei_days_remaining', 0)
    
    # Add these missing variables that were causing the error
    missed_pay = kwargs.get('missed_pay', 0)
    net_past_lost_wages = kwargs.get('net_past_lost_wages', calculation_details.get('Original Past Lost Wages', 
                                    calculation_details.get('Base Amount', 0)))
    
    # Open the template file
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Lost Wages Report for.docx')
    
    try:
        doc = Document(template_path)
    except Exception as e:
        print(f"Error opening template: {e}")
        # If template cannot be opened, create a new document
        doc = Document()
        doc.add_heading('PAST AND FUTURE WAGE LOSS', 0)
    
    # Format dates
    today_date = current_date.strftime("%B %d, %Y")
    loss_date_str = loss_date.strftime("%B %d, %Y") if loss_date else "Not specified"
    
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
    
    # Create a dictionary of replacements
    replacements = {
        "[CLIENT NAME]": client_name,
        "[Today's Date]": today_date,
        "[PROVINCE]": province_display,
        "[TAX YEAR]": str(current_date.year),
        "[GROSS INCOME]": f"${result.get('Gross Income', 0):,.2f}",
        "[FEDERAL TAXES]": f"${result.get('Federal Tax', 0):,.2f}",
        "[PROVINCIAL TAXES]": f"${result.get(f'{province.capitalize()} Tax', 0):,.2f}",
        "[CPP AMOUNT]": f"${result.get('CPP Contribution', 0) + result.get('CPP2 Contribution', 0):,.2f}",
        "[EI AMOUNT]": f"${result.get('EI Contribution', 0):,.2f}",
        "[DEPENDENT DEDUCTION]": f"${result.get('Dependent Benefit', 0):,.2f}",
        "[NET INCOME]": f"${result.get('Net Pay (Provincially specific deductions for damages)', 0):,.2f}",
        "[GROSS INCOME]": f"${result.get('Gross Income', 0):,.2f}",
        "[TIME PERIOD FOR PAST LOST WAGES]": f"{missed_time} {missed_time_unit}",
        "[TOTAL MISSED INCOME BEFORE PJI AND COLLATERAL BENEFITS]": f"${missed_pay:,.2f}" if isinstance(missed_pay, (int, float)) else f"${net_past_lost_wages:,.2f}",
    }
    
    # Past Lost Wages section
    replacements.update({
        "[TOTAL COLLATERAL BENEFITS RECEIVED TO DATE AMOUNT]": f"${collateral_benefits.get('Total Past Benefits', 0):,.2f}",
        "[DATE RANGE USED TO CALCULATE PJI]": f"{loss_date_str} to {today_date}",
        "[PJI Rate]": f"{calculation_details.get('PJI Rate', 2.5):.2f}%",
        "[PJI Amount]": f"${calculation_details.get('Interest Amount', 0):,.2f}",
        "[TOTAL PAST LOST WAGES AFTER PJI AND COLLATERAL BENEFITS]": f"${calculation_details.get('Past Lost Wages with Interest', 0):,.2f}"
    })
    
    # Add individual collateral benefits
    if collateral_benefits.get('EI Benefits (to date)', 0) > 0:
        replacements["[TOTAL COLLATERAL BENEFITS RECEIVED TO DATE AMOUNT]"] += f"\nEI Benefits: ${collateral_benefits.get('EI Benefits (to date)', 0):,.2f}"
    if collateral_benefits.get('Section B Benefits (to date)', 0) > 0:
        replacements["[TOTAL COLLATERAL BENEFITS RECEIVED TO DATE AMOUNT]"] += f"\nSection B Benefits: ${collateral_benefits.get('Section B Benefits (to date)', 0):,.2f}"
    if collateral_benefits.get('LTD Benefits (to date)', 0) > 0:
        replacements["[TOTAL COLLATERAL BENEFITS RECEIVED TO DATE AMOUNT]"] += f"\nLTD Benefits: ${collateral_benefits.get('LTD Benefits (to date)', 0):,.2f}"
    if collateral_benefits.get('CPPD Benefits (to date)', 0) > 0:
        replacements["[TOTAL COLLATERAL BENEFITS RECEIVED TO DATE AMOUNT]"] += f"\nCPPD Benefits: ${collateral_benefits.get('CPPD Benefits (to date)', 0):,.2f}"
    if collateral_benefits.get('Other Benefits (to date)', 0) > 0:
        replacements["[TOTAL COLLATERAL BENEFITS RECEIVED TO DATE AMOUNT]"] += f"\nOther Benefits: ${collateral_benefits.get('Other Benefits (to date)', 0):,.2f}"
    
    # Future Lost Wages section - only if requested
    if present_value_details.get('present_value', 0) > 0:
        replacements.update({
            "[NET INCOME]": f"${result.get('Net Pay (Provincially specific deductions for damages)', 0):,.2f}",
            "[RETURN TO WORK STATUS]": kwargs.get('return_status', "Not specified").capitalize(),
            "[TOTAL Annual Collateral Benefits Moving Forward]": f"${collateral_benefits.get('Total Annual Future Benefits', 0):,.2f}",
            "[DISCOUNT RATE PERCENTAGE]": f"{present_value_details.get('discount_rate', 0) * 100:.2f}%",
            "[Future Lost Wages Time Horizon]": f"{present_value_details.get('time_horizon', 0):.2f} years",
            "[TOTAL FUTURE LOST WAGES AMOUNT]": f"${present_value_details.get('present_value', 0):,.2f}"
        })
        
        # Add individual future collateral benefits
        if collateral_benefits.get('EI Benefits (annual)', 0) > 0:
            replacements["[TOTAL Annual Collateral Benefits Moving Forward]"] += f"\nEI Benefits: ${collateral_benefits.get('EI Benefits (annual)', 0):,.2f}"
        if collateral_benefits.get('Section B Benefits (annual)', 0) > 0:
            replacements["[TOTAL Annual Collateral Benefits Moving Forward]"] += f"\nSection B Benefits: ${collateral_benefits.get('Section B Benefits (annual)', 0):,.2f}"
        if collateral_benefits.get('LTD Benefits (annual)', 0) > 0:
            replacements["[TOTAL Annual Collateral Benefits Moving Forward]"] += f"\nLTD Benefits: ${collateral_benefits.get('LTD Benefits (annual)', 0):,.2f}"
        if collateral_benefits.get('CPPD Benefits (annual)', 0) > 0:
            replacements["[TOTAL Annual Collateral Benefits Moving Forward]"] += f"\nCPPD Benefits: ${collateral_benefits.get('CPPD Benefits (annual)', 0):,.2f}"
        if collateral_benefits.get('Other Benefits (annual)', 0) > 0:
            replacements["[TOTAL Annual Collateral Benefits Moving Forward]"] += f"\nOther Benefits: ${collateral_benefits.get('Other Benefits (annual)', 0):,.2f}"
        
        # Conditional Fields
        if "returning to work" in str(kwargs.get('return_status', "")).lower():
            replacements["[**Speculative Return to Work Date**]"] = kwargs.get('end_date', "Not specified").strftime("%B %d, %Y") if hasattr(kwargs.get('end_date', ""), 'strftime') else str(kwargs.get('end_date', "Not specified"))
        else:
            replacements["[**Speculative Return to Work Date**]"] = "Not applicable (Total Disability)"
        
        if "total disability" in str(kwargs.get('return_status', "")).lower():
            if birthdate:
                replacements["[Date of Birth]"] = birthdate.strftime("%B %d, %Y")
            else:
                replacements["[Date of Birth]"] = "Not specified"
                
            replacements["[Retirement Age]"] = str(retirement_age) if retirement_age else "65"
    
    # Total Wage Loss section
    replacements.update({
        "[TOTAL PAST LOST WAGES]": f"${calculation_details.get('Past Lost Wages with Interest', 0):,.2f}",
        "[TOTAL FUTURE LOST WAGES]": f"${present_value_details.get('present_value', 0):,.2f}",
        "[Total Economic Damages]": f"${calculation_details.get('Past Lost Wages with Interest', 0) + present_value_details.get('present_value', 0):,.2f}"
    })
    
    # Notes
    provincial_notes = ""
    if province.lower() == "nova scotia":
        provincial_notes = "In Nova Scotia, CPP, EI, and income taxes are deducted when calculating net income for damages."
    elif province.lower() == "new brunswick":
        provincial_notes = "In New Brunswick, federal and provincial income taxes are deducted, but CPP and EI are NOT deducted for damages calculations."
    elif province.lower() == "prince edward island":
        provincial_notes = "PEI calculates damages based on gross income rather than net income."
    elif province.lower() == "newfoundland" or province.lower() == "newfoundland and labrador":
        provincial_notes = "Newfoundland follows the standard 'net income' approach with province-specific tax calculations."
    
    pji_note = f"PJI Rate was calculated using T-Bill rates for the period from {loss_date_str} to {today_date}"
    discount_rate_note = f"Discount rate of {present_value_details.get('discount_rate', 0) * 100:.2f}% is used as per {province_display} standards"
    
    # Add notes
    replacements["[NOTE on HOW PJI Rate Was calculate]"] = pji_note
    replacements["[NOTE ON ANY PROVICIALLY SPECIFIC REASONING ON DEDUCTIONS]"] = provincial_notes
    replacements["[NOTE ON HOW DISCOUNT RATE WAS CALCULATED]"] = discount_rate_note
    replacements["[NOTE ANY PROVINCIALLY SPECIFIC REASONING]"] = provincial_notes
    
    if ei_days_remaining > 0:
        replacements["[NOTE EI SICK BENIFITS CUT OFF IF APPLICABLE]"] = f"EI sickness benefits are limited to 26 weeks (182 days). {ei_days_remaining} days remaining."
    else:
        replacements["[NOTE EI SICK BENIFITS CUT OFF IF APPLICABLE]"] = "EI sickness benefits period has been fully utilized."
    
    # Process the document to replace placeholders
    for paragraph in doc.paragraphs:
        for key, value in replacements.items():
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, str(value))
    
    # Also process tables for replacements
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for key, value in replacements.items():
                        if key in paragraph.text:
                            paragraph.text = paragraph.text.replace(key, str(value))
    
    # Remove conditional sections that are not applicable
    if present_value_details.get('present_value', 0) == 0:
        # Find and remove the future lost wages section
        new_paragraphs = []
        skip_mode = False
        
        for paragraph in doc.paragraphs:
            if "*ONLY SHOW THIS IF THEY ASKED TO CALCULATE FUTURE LOST WAGES*" in paragraph.text:
                skip_mode = True
                continue
            
            if skip_mode and "**TOTAL WAGE LOSS**" in paragraph.text:
                skip_mode = False
                
            if not skip_mode:
                new_paragraphs.append(paragraph)
    
    # Check if returning to work or total disability and handle conditional fields
    return_status = str(kwargs.get('return_status', "")).lower()
    for paragraph in doc.paragraphs:
        # Handle returning to work conditional
        if "*ONLY IF RETURN TO WORK STATUS IS Returning to Work*" in paragraph.text:
            if "returning to work" not in return_status:
                paragraph.text = ""  # Clear if not applicable
            else:
                paragraph.text = paragraph.text.replace("*ONLY IF RETURN TO WORK STATUS IS Returning to Work*", "")
        
        # Handle total disability conditional
        if "*ONLY IF RETURN TO WORK STATUS IS TOTAL DISABILITY*" in paragraph.text:
            if "total disability" not in return_status:
                paragraph.text = ""  # Clear if not applicable
            else:
                paragraph.text = paragraph.text.replace("*ONLY IF RETURN TO WORK STATUS IS TOTAL DISABILITY*", "")
    
    # Save the document
    try:
        doc.save(output_path)
        print(f"Word document saved successfully at: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error saving Word document: {e}")
        return None
