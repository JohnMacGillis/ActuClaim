def get_available_tax_years():
    return [2023, 2024, 2025]

def get_tax_rates(year, province):
    return {
        "federal": {
            "brackets": [0, 15000, 50000, 100000, 150000, 200000],
            "rates": [0.0, 0.15, 0.205, 0.26, 0.29, 0.33]
        },
        "provincial": {
            "brackets": [0, 10000, 30000, 60000, 100000, 150000],
            "rates": [0.0, 0.08, 0.14, 0.16, 0.17, 0.20]
        }
    }

def calculate_tax(income, year, province):
    return {
        "federal_tax": income * 0.15,
        "provincial_tax": income * 0.10,
        "total_tax": income * 0.25,
        "effective_rate": 0.25
    }

def calculate_bracket_tax(income, brackets, rates):
    tax = 0
    for i in range(len(brackets)-1):
        if income > brackets[i]:
            bracket_income = min(income, brackets[i+1]) - brackets[i]
            tax += bracket_income * rates[i]
    if income > brackets[-1] and len(brackets) == len(rates):
        tax += (income - brackets[-1]) * rates[-1]
    return tax
