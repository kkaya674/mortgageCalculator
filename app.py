from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import json

app = Flask(__name__)

def run_simulation(params):
    """Run the mortgage simulation with given parameters"""
    
    # Extract parameters
    HOME_PRICE = float(params['home_price'])
    DOWN_PAYMENT_PERCENTAGE = float(params['down_payment_percentage']) / 100
    LOAN_TERM_YEARS = int(params['loan_term_years'])
    INTEREST_RATE_ANNUAL = float(params['interest_rate_annual']) / 100
    HOME_APPRECIATION_RATE_ANNUAL = float(params['home_appreciation_rate_annual']) / 100
    RENTAL_SAVINGS_ANNUAL = float(params['rental_savings_annual']) * 12
    ANNUAL_COSTS = float(params['annual_costs'])
    RENTAL_INCREASE_RATE_ANNUAL = float(params['rental_increase_rate_annual']) / 100
    ESTATE_AGENT_FEE_PERCENTAGE = float(params['estate_agent_fee_percentage']) / 100
    NOTARY_FEE_PERCENTAGE = float(params['notary_fee_percentage']) / 100
    PURCHASE_TAX_PERCENTAGE = float(params['purchase_tax_percentage']) / 100
    SIMULATION_YEARS = int(params['simulation_years'])
    
    # Initial calculations
    DOWN_PAYMENT_AMOUNT = HOME_PRICE * DOWN_PAYMENT_PERCENTAGE
    LOAN_PRINCIPAL = HOME_PRICE - DOWN_PAYMENT_AMOUNT
    INTEREST_RATE_MONTHLY = INTEREST_RATE_ANNUAL / 12
    TOTAL_PAYMENTS = LOAN_TERM_YEARS * 12
    
    # Calculate monthly mortgage payment
    if INTEREST_RATE_MONTHLY > 0:
        monthly_payment = LOAN_PRINCIPAL * (INTEREST_RATE_MONTHLY * (1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS) / ((1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS - 1)
    else:
        monthly_payment = LOAN_PRINCIPAL / TOTAL_PAYMENTS
    
    # Calculate one-time purchase costs
    estate_agent_fee = HOME_PRICE * ESTATE_AGENT_FEE_PERCENTAGE
    notary_fee = HOME_PRICE * NOTARY_FEE_PERCENTAGE
    purchase_tax = HOME_PRICE * PURCHASE_TAX_PERCENTAGE
    total_one_time_costs = estate_agent_fee + notary_fee + purchase_tax
    
    # Calculate total interest for loan
    total_loan_payments = monthly_payment * TOTAL_PAYMENTS
    total_interest_for_loan = total_loan_payments - LOAN_PRINCIPAL
    
    # Annual simulation
    simulation_results = []
    cumulative_rent_saved = 0
    current_annual_rent = RENTAL_SAVINGS_ANNUAL
    
    for year in range(1, SIMULATION_YEARS + 1):
        cumulative_rent_saved += current_annual_rent
        
        current_home_value = HOME_PRICE * (1 + HOME_APPRECIATION_RATE_ANNUAL)**year
        home_value_appreciation = current_home_value - HOME_PRICE
        total_costs_paid = ANNUAL_COSTS * year
        
        if year <= LOAN_TERM_YEARS:
            payments_made = year * 12
            if INTEREST_RATE_MONTHLY > 0:
                remaining_balance = LOAN_PRINCIPAL * ((1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS - (1 + INTEREST_RATE_MONTHLY)**payments_made) / ((1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS - 1)
            else:
                remaining_balance = LOAN_PRINCIPAL * (1 - (payments_made / TOTAL_PAYMENTS))
            
            total_paid = monthly_payment * payments_made
            principal_paid = LOAN_PRINCIPAL - remaining_balance
            interest_paid = total_paid - principal_paid
        else:
            interest_paid = total_interest_for_loan
        
        net_profit = home_value_appreciation + cumulative_rent_saved - interest_paid - total_costs_paid - total_one_time_costs
        
        simulation_results.append({
            "year": year,
            "net_profit": net_profit,
            "current_home_value": current_home_value,
            "interest_paid": interest_paid,
            "home_value_appreciation": home_value_appreciation,
            "total_rent_saved": cumulative_rent_saved
        })
        
        current_annual_rent *= (1 + RENTAL_INCREASE_RATE_ANNUAL)
    
    # Find optimal year
    best_year_data = max(simulation_results, key=lambda x: x['net_profit'])
    optimal_year = best_year_data['year']
    max_profit = best_year_data['net_profit']
    
    # Monthly breakdown for graphs
    months_axis = np.arange(1, SIMULATION_YEARS * 12 + 1)
    remaining_balance_monthly = []
    interest_paid_monthly = []
    principal_paid_monthly = []
    total_payment_monthly = []
    rent_monthly_list = []
    
    current_balance = LOAN_PRINCIPAL
    for month_num in months_axis:
        if month_num <= TOTAL_PAYMENTS:
            interest_for_month = current_balance * INTEREST_RATE_MONTHLY
            principal_for_month = monthly_payment - interest_for_month
            current_balance -= principal_for_month
            if current_balance < 0: current_balance = 0
            payment_this_month = monthly_payment
        else:
            interest_for_month = 0
            principal_for_month = 0
            current_balance = 0
            payment_this_month = 0
        
        current_year_index = (month_num - 1) // 12
        rent_this_month = (RENTAL_SAVINGS_ANNUAL * (1 + RENTAL_INCREASE_RATE_ANNUAL)**current_year_index) / 12
        rent_monthly_list.append(rent_this_month)
        
        remaining_balance_monthly.append(current_balance)
        interest_paid_monthly.append(interest_for_month)
        principal_paid_monthly.append(principal_for_month)
        total_payment_monthly.append(payment_this_month)
    
    # Cash flow simulation
    initial_bank_balance = 0 - (DOWN_PAYMENT_AMOUNT + estate_agent_fee + notary_fee + purchase_tax)
    bank_balance = [initial_bank_balance]
    monthly_costs = ANNUAL_COSTS / 12
    
    for month_num in range(1, SIMULATION_YEARS * 12 + 1):
        current_year_index = (month_num - 1) // 12
        rent_this_month = (RENTAL_SAVINGS_ANNUAL * (1 + RENTAL_INCREASE_RATE_ANNUAL)**current_year_index) / 12
        
        if month_num <= TOTAL_PAYMENTS:
            loan_payment = monthly_payment
        else:
            loan_payment = 0
        
        net_cash = rent_this_month - loan_payment - monthly_costs
        bank_balance.append(bank_balance[-1] + net_cash)
    
    return {
        'simulation_results': simulation_results,
        'optimal_year': optimal_year,
        'max_profit': max_profit,
        'monthly_data': {
            'months': months_axis.tolist(),
            'remaining_balance': remaining_balance_monthly,
            'interest_paid': interest_paid_monthly,
            'principal_paid': principal_paid_monthly,
            'total_payment': total_payment_monthly,
            'rent_monthly': rent_monthly_list,
            'bank_balance': bank_balance
        },
        'summary': {
            'home_price': HOME_PRICE,
            'down_payment': DOWN_PAYMENT_AMOUNT,
            'loan_principal': LOAN_PRINCIPAL,
            'monthly_payment': monthly_payment,
            'total_one_time_costs': total_one_time_costs,
            'estate_agent_fee': estate_agent_fee,
            'notary_fee': notary_fee,
            'purchase_tax': purchase_tax
        }
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    result = run_simulation(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 