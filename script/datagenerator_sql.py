import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sqlalchemy
import urllib

random.seed(42)

def generate_messy_data(num_rows=2500):
    SERVER_NAME = r'LOCALHOST\SQLEXPRESS' 
    DATABASE_NAME = 'FinancePortfolioDB'
    
    cities = {
        'Windsor': ('Ontario', 'Canada', 42.3149, -83.0364),
        'Toronto': ('Ontario', 'Canada', 43.6532, -79.3832),
        'Detroit': ('Michigan', 'United States', 42.3314, -83.0458),
        'Kitchener': ('Ontario', 'Canada', 43.4516, -80.4925),
        'Ottawa': ('Ontario', 'Canada', 45.4215, -75.6972),
    }
    payment_modes = ['Credit Card', 'Debit Card', 'E-Transfer', 'Cash']
    categories = {
        'Expense': ['Rent', 'Groceries', 'Utilities', 'Dining', 'Tech', 'Transport', 'Cybersecurity', 'Entertainment', 'Healthcare'],
        'Income': ['Salary', 'Freelance', 'Investments', 'Gift']
    }

    # 1. GENERATE MESSY TRANSACTIONS
    start_date = datetime(2025, 1, 1)
    actuals_list = []
    
    for _ in range(num_rows):
        type_choice = random.choices(['Expense', 'Income'], weights=[0.82, 0.18])[0]
        category = random.choice(categories[type_choice])
        date = start_date + timedelta(days=random.randint(0, 450))
        amt = 1200.00 if category == 'Rent' else round(random.uniform(10, 400), 2)
        
        city = random.choice(list(cities.keys()))
        province, country, lat, lon = cities[city]
        
        # --- INJECTING MESSY DATA (TRANSACTIONS) ---
        if random.random() < 0.08:
            city = city.lower()
        if random.random() < 0.05:
            city = city + " " 
            
        if random.random() < 0.03:
            amt = None
            
        txn_id = f"TXN-{random.randint(100000, 100800)}" 

        actuals_list.append([
            date, category, type_choice, amt,
            city, province, country, lat, lon, random.choice(payment_modes), txn_id
        ])

    df_actuals = pd.DataFrame(actuals_list, columns=['Date', 'Category', 'Type', 'Amount', 'City', 'Province', 'Country', 'Latitude', 'Longitude', 'PaymentMode', 'TransactionID'])
    df_actuals['Date'] = pd.to_datetime(df_actuals['Date'])

    # 2. GENERATE MESSY BUDGET DATA
    budget_list = []
    monthly_targets = {
        'Groceries': 500, 'Dining': 300, 'Utilities': 200, 'Tech': 150, 
        'Transport': 250, 'Cybersecurity': 100, 'Entertainment': 100, 
        'Healthcare': 80, 'Rent': 1200
    }
    
    for year in [2025, 2026]:
        for month in range(1, 13):
            for cat, target in monthly_targets.items():
                
                # --- INJECTING MESSY DATA (BUDGET MISMATCHES) ---
                dirty_cat = cat
                if random.random() < 0.15: # 15% chance the finance team typed it wrong
                    if cat == 'Tech': dirty_cat = 'Technology'
                    elif cat == 'Dining': dirty_cat = 'Food & Bev'
                    elif cat == 'Cybersecurity': dirty_cat = 'InfoSec'
                    elif cat == 'Groceries': dirty_cat = 'Grocery'
                    
                budget_list.append([datetime(year, month, 1), dirty_cat, target])
                
    df_budget = pd.DataFrame(budget_list, columns=['BudgetMonth', 'Category', 'BudgetAmount'])
    df_budget['BudgetMonth'] = pd.to_datetime(df_budget['BudgetMonth'])

    # 3. PUSH BOTH TO SQL SERVER
    print(f"Connecting to SQL Server: {SERVER_NAME}...")
    params = urllib.parse.quote_plus(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;")
    engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

    try:
        df_actuals.to_sql('Fact_Transactions_Messy', engine, if_exists='replace', index=False, dtype={'Date': sqlalchemy.DateTime()})
        print("SUCCESS: Messy Data uploaded to [Fact_Transactions_Messy].")
        
        df_budget.to_sql('Fact_Budget_Messy', engine, if_exists='replace', index=False, dtype={'BudgetMonth': sqlalchemy.DateTime()})
        print("SUCCESS: Messy Budget Data uploaded to [Fact_Budget_Messy].")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_messy_data(2500)