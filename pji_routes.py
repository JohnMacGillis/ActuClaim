from flask import Blueprint, request, render_template, jsonify
from datetime import datetime
from pji_calculator import calculate_pji

# Create a Blueprint for PJI routes
pji_routes = Blueprint('pji', __name__)

@pji_routes.route('/calculate-pji', methods=['POST'])
def api_calculate_pji():
    """API endpoint to calculate PJI"""
    data = request.json
    
    # Extract required parameters
    loss_date = data.get('loss_date')
    calculation_date = data.get('calculation_date', datetime.now().strftime('%Y-%m-%d'))
    amount = float(data.get('amount', 0))
    
    # Validate parameters
    if not loss_date:
        return jsonify({'error': 'Loss date is required'}), 400
    
    try:
        # Calculate PJI using T-Bill rates
        result = calculate_pji(loss_date, calculation_date, amount)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pji_routes.route('/pji-calculator', methods=['GET'])
def pji_calculator_page():
    """Render the PJI calculator page"""
    return render_template('pji_calculator.html')

# Integration with frontend using AJAX
@pji_routes.route('/api/tbill-rate', methods=['GET'])
def get_tbill_rate():
    """Get the T-Bill rate for a specific date range"""
    from tbill_utils import get_average_tbill_rate
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    if not start_date:
        return jsonify({'error': 'Start date is required'}), 400
    
    try:
        rate = get_average_tbill_rate(start_date, end_date)
        return jsonify({'rate': rate})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
