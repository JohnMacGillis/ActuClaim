# =============================================================================
# TAX CALCULATION FUNCTIONS
# =============================================================================

def calculate_dependent_benefit(dependents):
    """Calculate dependent benefit based on number of dependents under 18."""
    # $2,616 per dependent, max of $8,375
    benefit = min(int(dependents) * 2616, 8375)
    return benefit

def calculate_federal_tax(income, dependents=0):
    """Calculate federal tax based on income level and dependents."""
    # Calculate dependent benefit
    dependent_benefit = calculate_dependent_benefit(dependents)
    
    # Reduce taxable income by dependent benefit
    taxable_income = max(income - dependent_benefit, 0)
    
    federal_brackets = [
        (0, 15705, 0.00),
        (15705, 55867, 0.15),
        (55867, 111733, 0.205),
        (111733, 173205, 0.26),
        (173205, 246752, 0.29),
        (246752, float('inf'), 0.33)
    ]
    
    federal_tax = 0
    for lower, upper, rate in federal_brackets:
        if taxable_income > lower:
            taxable_income_in_bracket = min(taxable_income, upper) - lower
            federal_tax += taxable_income_in_bracket * rate
        else:
            break
    return federal_tax

def calculate_cpp_contributions(income):
    """Calculate Canada Pension Plan contributions."""
    cpp_rate = 0.0595  
    cpp_max_earnings = 68500
    cpp_exemption = 3500

    cpp2_rate = 0.04  
    cpp2_max_earnings = 73200

    cpp_contribution = min((min(income, cpp_max_earnings) - cpp_exemption) * cpp_rate, (cpp_max_earnings - cpp_exemption) * cpp_rate) if income > cpp_exemption else 0
    cpp2_contribution = min((min(income, cpp2_max_earnings) - cpp_max_earnings) * cpp2_rate, (cpp2_max_earnings - cpp_max_earnings) * cpp2_rate) if income > cpp_max_earnings else 0

    return round(cpp_contribution, 2), round(cpp2_contribution, 2)

def calculate_ei_contribution(income):
    """Calculate Employment Insurance contribution."""
    ei_rate = 0.0166  
    ei_max_earnings = 63200  
    return round(min(income, ei_max_earnings) * ei_rate, 2)

def calculate_provincial_tax(income, province, dependents=0):
    """Calculate provincial tax based on income level, province, and dependents."""
    # Calculate dependent benefit
    dependent_benefit = calculate_dependent_benefit(dependents)
    
    # Reduce taxable income by dependent benefit
    taxable_income = max(income - dependent_benefit, 0)
    
    tax_brackets = {
        "nova scotia": [
            (0, 8481, 0.00),
            (8481, 29590, 0.0879),
            (29590, 59180, 0.1495),
            (59180, 93000, 0.1667),
            (93000, 150000, 0.175),
            (150000, float('inf'), 0.21)
        ],
        "newfoundland": [
            (0, 10818, 0.00),
            (10818, 43198, 0.087),
            (43198, 86395, 0.145),
            (86395, 154244, 0.158),
            (154244, 215943, 0.178),
            (215943, 275870, 0.198),
            (275870, 551739, 0.208),
            (551739, 1103478, 0.213),
            (1103478, float('inf'), 0.218)
        ],
        "new brunswick": [
            (0, 13044, 0.00),
            (13044, 49958, 0.094),
            (49958, 99916, 0.14),
            (99916, 185064, 0.16),
            (185064, float('inf'), 0.195)
        ],
        "prince edward island": [
            (0, 14250, 0.00),
            (14250, 32656, 0.0965),
            (32656, 64313, 0.1363),
            (64313, 105000, 0.1665),
            (105000, 140000, 0.18),
            (140000, float('inf'), 0.1875)
        ]
    }
    
    provincial_tax = 0
    for lower, upper, rate in tax_brackets[province]:
        if taxable_income > lower:
            taxable_amount = min(taxable_income, upper) - lower
            provincial_tax += taxable_amount * rate
        else:
            break
    return provincial_tax
