import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# 📌 Inputs (Scenario)
# -----------------------------
HOME_PRICE = 195000
DOWN_PAYMENT_PERCENTAGE = 0.10
# The full term of the mortgage loan in years
LOAN_TERM_YEARS = 10
# Annual mortgage interest rate (e.g., 3%)
INTEREST_RATE_ANNUAL = 0.0325
# Expected annual home value appreciation rate (e.g., 2%)
HOME_APPRECIATION_RATE_ANNUAL = INTEREST_RATE_ANNUAL*0.02/0.0325
# Annual savings from not renting (e.g., 1200/month * 12)
RENTAL_SAVINGS_ANNUAL = 1000 * 12
# Annual costs like property tax, insurance, and maintenance
ANNUAL_COSTS = 1500
# Expected annual increase in rent (e.g., 5%)
RENTAL_INCREASE_RATE_ANNUAL =INTEREST_RATE_ANNUAL* 0.02/0.0325
# --- One-time Purchase Costs (Percentages of Home Price) ---
ESTATE_AGENT_FEE_PERCENTAGE = 0.0357
NOTARY_FEE_PERCENTAGE = 0.02
PURCHASE_TAX_PERCENTAGE = 0.06
# How many years to simulate for the decision
SIMULATION_YEARS = 15

# ---------------------------------
# 🏦 Initial Calculations
# ---------------------------------
DOWN_PAYMENT_AMOUNT = HOME_PRICE * DOWN_PAYMENT_PERCENTAGE
LOAN_PRINCIPAL = HOME_PRICE - DOWN_PAYMENT_AMOUNT
INTEREST_RATE_MONTHLY = INTEREST_RATE_ANNUAL / 12
TOTAL_PAYMENTS = LOAN_TERM_YEARS * 12

# Calculate monthly mortgage payment (M) using the formula:
# M = P * [r(1+r)^n] / [(1+r)^n - 1]
if INTEREST_RATE_MONTHLY > 0:
    monthly_payment = LOAN_PRINCIPAL * (INTEREST_RATE_MONTHLY * (1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS) / ((1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS - 1)
else:
    monthly_payment = LOAN_PRINCIPAL / TOTAL_PAYMENTS

# --- Calculate One-Time Purchase Costs ---
estate_agent_fee = HOME_PRICE * ESTATE_AGENT_FEE_PERCENTAGE
notary_fee = HOME_PRICE * NOTARY_FEE_PERCENTAGE
purchase_tax = HOME_PRICE * PURCHASE_TAX_PERCENTAGE
total_one_time_costs = estate_agent_fee + notary_fee + purchase_tax

# Calculate the total interest paid over the entire loan term
total_loan_payments = monthly_payment * TOTAL_PAYMENTS
total_interest_for_loan = total_loan_payments - LOAN_PRINCIPAL

# ----------------------------------------------------
# 📈 Simulation: Calculate Net Profit Over the Years
# ----------------------------------------------------
simulation_results = []
cumulative_rent_saved = 0
current_annual_rent = RENTAL_SAVINGS_ANNUAL

for year in range(1, SIMULATION_YEARS + 1):
    # Add this year's rent to the cumulative total
    cumulative_rent_saved += current_annual_rent

    current_home_value = HOME_PRICE * (1 + HOME_APPRECIATION_RATE_ANNUAL)**year
    home_value_appreciation = current_home_value - HOME_PRICE
    total_costs_paid = ANNUAL_COSTS * year

    # Calculate interest paid depending on whether the loan is active
    if year <= LOAN_TERM_YEARS:
        payments_made = year * 12
        # Calculate remaining loan balance to find principal and interest paid so far
        if INTEREST_RATE_MONTHLY > 0:
            remaining_balance = LOAN_PRINCIPAL * ((1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS - (1 + INTEREST_RATE_MONTHLY)**payments_made) / ((1 + INTEREST_RATE_MONTHLY)**TOTAL_PAYMENTS - 1)
        else:
            remaining_balance = LOAN_PRINCIPAL * (1 - (payments_made / TOTAL_PAYMENTS))
        
        total_paid = monthly_payment * payments_made
        principal_paid = LOAN_PRINCIPAL - remaining_balance
        interest_paid = total_paid - principal_paid
    else: # Loan is paid off
        interest_paid = total_interest_for_loan # Interest cost is now a fixed historical value

    # Net Profit = (Appreciation + Rent Saved) - (Interest + Annual Costs + One-Time Costs)
    net_profit = home_value_appreciation + cumulative_rent_saved - interest_paid - total_costs_paid - total_one_time_costs

    simulation_results.append({
        "year": year,
        "net_profit": net_profit,
        "current_home_value": current_home_value,
        "interest_paid": interest_paid,
        "home_value_appreciation": home_value_appreciation,
        "total_rent_saved": cumulative_rent_saved
    })

    # Increase the rent for the next year
    current_annual_rent *= (1 + RENTAL_INCREASE_RATE_ANNUAL)

# Find the year with the maximum net profit
best_year_data = max(simulation_results, key=lambda x: x['net_profit'])
optimal_year = best_year_data['year']
max_profit = best_year_data['net_profit']

# -----------------------------
# 📝 Generate TXT Report for the Optimal Year
# -----------------------------
report = f"""
Mortgage Profitability Simulation - Report

Scenario:
- Home Price: €{HOME_PRICE:,.2f}
- Down Payment: €{DOWN_PAYMENT_AMOUNT:,.2f} ({DOWN_PAYMENT_PERCENTAGE:.0%})
- Loan Amount: €{LOAN_PRINCIPAL:,.2f}
- Loan Term: {LOAN_TERM_YEARS} years at {INTEREST_RATE_ANNUAL:.2%} interest

Initial One-Time Costs:
- Estate Agent Fee (3.57%): -€{estate_agent_fee:,.2f}
- Notary Fee (2.00%):      -€{notary_fee:,.2f}
- Purchase Tax (6.00%):      -€{purchase_tax:,.2f}
---------------------------------
- Total One-Time Costs:    -€{total_one_time_costs:,.2f}

Optimal Year to Sell: Year {optimal_year}
--------------------------------------------------
💰 Maximum Net Advantage (vs. Renting): €{max_profit:,.2f}

Details for Year {optimal_year}:
📈 Home Value Appreciation   : +€{best_year_data['home_value_appreciation']:,.2f} (New Value: €{best_year_data['current_home_value']:,.2f})
🏠 Avoided Rent Cost         : +€{best_year_data['total_rent_saved']:,.2f}
💸 Interest Paid (Cumulative): -€{best_year_data['interest_paid']:,.2f}
🏛️ Annual Costs (Cumulative) : -€{ANNUAL_COSTS * optimal_year:,.2f}
"""

with open("mortgage_simulation_report.txt", "w", encoding="utf-8") as f:
    f.write(report)

print(report)

# -----------------------------
# 📊 Grafik 1: Net Avantaj Simülasyonu (Kiralama Kıyaslı)
# -----------------------------
years = [res['year'] for res in simulation_results]
profits = [res['net_profit'] for res in simulation_results]

plt.figure(figsize=(10, 6))
plt.plot(years, profits, marker='o', label="Net Avantaj (Kiralama Kıyaslı)")
plt.axvline(x=optimal_year, color='r', linestyle='--', label=f"Optimal Yıl: {optimal_year} (€{max_profit:,.0f})")
plt.title("Net Avantaj Simülasyonu: Ev Sahibi Olmanın Kiralamaya Göre Avantajı")
plt.xlabel("Satış Yılı")
plt.ylabel("Kümülatif Net Avantaj (€)")
plt.grid(True)
plt.axhline(0, color='black', linewidth=0.5, linestyle='-')
plt.legend()
plt.tight_layout()
plt.savefig("net_avantaj_simulasyonu.png")
plt.show()


# ----------------------------------------------------
# 📉 Aylık Döküm için Amortisman Hesaplanması
# ----------------------------------------------------
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
        if current_balance < 0: current_balance = 0 # Prevent negative balance from float errors
        payment_this_month = monthly_payment
    else: # Loan is paid off
        interest_for_month = 0
        principal_for_month = 0
        current_balance = 0
        payment_this_month = 0

    # Calculate rent for the current month, including annual increases
    current_year_index = (month_num - 1) // 12
    rent_this_month = (RENTAL_SAVINGS_ANNUAL * (1 + RENTAL_INCREASE_RATE_ANNUAL)**current_year_index) / 12
    rent_monthly_list.append(rent_this_month)

    remaining_balance_monthly.append(current_balance)
    interest_paid_monthly.append(interest_for_month)
    principal_paid_monthly.append(principal_for_month)
    total_payment_monthly.append(payment_this_month)

# RENTAL_SAVINGS_MONTHLY is no longer used as a single constant

# -----------------------------
# 📊 Grafik 2: Aylık Finansal Detaylar
# -----------------------------
fig, ax1 = plt.subplots(figsize=(12, 7))

# Sol Y Ekseni (ax1)
ax1.set_xlabel('Aylar')
ax1.set_ylabel('Aylık Miktar (€)')
p1, = ax1.plot(months_axis, interest_paid_monthly, 'r-', label='Aylık Faiz Ödemesi')
p2, = ax1.plot(months_axis, principal_paid_monthly, 'g-', label='Aylık Anapara Ödemesi')
p3, = ax1.plot(months_axis, rent_monthly_list, 'b--', label='Kaçınılan Aylık Kira (Yıllık Artışlı)')
# Toplam aylık ödeme artık bir liste olarak çiziliyor
p4, = ax1.plot(months_axis, total_payment_monthly, 'k-.', label='Toplam Aylık Ödeme')
ax1.grid(True)
ax1.set_ylim(bottom=0)

# Sağ Y Ekseni (ax2)
ax2 = ax1.twinx()
p5, = ax2.plot(months_axis, remaining_balance_monthly, 'm-', label='Kalan Kredi Borcu')
ax2.set_ylabel('Kalan Kredi Borcu (€)')
ax2.set_ylim(bottom=0)

# Başlık ve legend
plt.title('Aylık Ödeme Detayları ve Kaçınılan Kira Maliyeti')
plots = [p1, p2, p3, p4, p5]
ax1.legend(plots, [p.get_label() for p in plots], loc='upper center', bbox_to_anchor=(0.5, 1.17), ncol=3, fancybox=True)

plt.tight_layout()
plt.savefig("aylik_detaylar.png")
plt.show()

# -----------------------------
# 📊 Grafik 3: Kümülatif Nakit Akışı (Ev Satılmadan)
# -----------------------------

initial_bank_balance = 0 - (DOWN_PAYMENT_AMOUNT + estate_agent_fee + notary_fee + purchase_tax)
bank_balance = [initial_bank_balance]

monthly_costs = ANNUAL_COSTS / 12

for month_num in range(1, SIMULATION_YEARS * 12 + 1):
    # Kira geliri (pozitif)
    current_year_index = (month_num - 1) // 12
    rent_this_month = (RENTAL_SAVINGS_ANNUAL * (1 + RENTAL_INCREASE_RATE_ANNUAL)**current_year_index) / 12
    # Kredi taksiti (negatif, sadece kredi süresince)
    if month_num <= TOTAL_PAYMENTS:
        loan_payment = monthly_payment
    else:
        loan_payment = 0
    # Aylık net nakit akışı
    net_cash = rent_this_month - loan_payment - monthly_costs
    # Yeni bakiye
    bank_balance.append(bank_balance[-1] + net_cash)

months_axis = np.arange(0, SIMULATION_YEARS * 12 + 1)

plt.figure(figsize=(12, 7))
plt.plot(months_axis, bank_balance, label='Banka Bakiyesi (Kümülatif)', color='purple')
plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.title('Ev Satılmadan Kümülatif Nakit Akışı')
plt.xlabel('Ay')
plt.ylabel('Banka Bakiyesi (€)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('kumulatif_nakit_akisi.png')
plt.show()
