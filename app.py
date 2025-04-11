from flask import Flask, render_template, request, redirect, jsonify
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

DATA_FILE = 'expenses.json'

def load_expenses():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_expenses(expenses):
    with open(DATA_FILE, 'w') as f:
        json.dump(expenses, f, indent=4)

def prepare_data(expenses):
    # Convert expenses to a DataFrame
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # Group by month and year to get total spending per month
    monthly_expenses = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    monthly_expenses['time_index'] = np.arange(len(monthly_expenses))  # Create a time index for regression

    return monthly_expenses[['time_index', 'amount']], monthly_expenses['amount']

def train_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_future_spending(model, months_ahead=1):
    future_index = np.array([[len(X) + i] for i in range(1, months_ahead + 1)])
    predictions = model.predict(future_index)
    return predictions

def generate_suggestions(category_totals, total):
    suggestions = []
    for category, amount in category_totals.items():
        percentage = (amount / total) * 100 if total > 0 else 0
        if percentage > 50:
            suggestions.append(f"You are spending {percentage:.2f}% of your total expenses on {category}. Consider reducing your spending in this category.")
        elif percentage < 20:
            suggestions.append(f"You are spending only {percentage:.2f}% of your total expenses on {category}. Great job keeping your spending low in this category!")
    
    if total > 0:
        average_spending = total / len(category_totals)
        suggestions.append(f"Your average spending is ₹{average_spending:.2f}. Try to keep your expenses below this average to save more.")
    
    return suggestions

# Existing index route
@app.route('/', methods=['GET', 'POST'])
def index():
    expenses = load_expenses()
    total = sum(expense['amount'] for expense in expenses)

    # Summarize expenses by category
    category_totals = {}
    for expense in expenses:
        category = expense['category']
        amount = expense['amount']
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    # Generate suggestions based on spending
    suggestions = generate_suggestions(category_totals, total)

    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']

        if not date or not category or not amount or float(amount) <= 0:
            error_message = "Please provide valid inputs."
            return render_template('index.html', expenses=expenses, total=total, error=error_message, category_totals=category_totals, suggestions=suggestions)

        expenses.append({
            'date': date,
            'category': category,
            'amount': float(amount)
        })
        save_expenses(expenses)
        return redirect('/')

    return render_template('index.html', expenses=expenses, total=total, category_totals=category_totals, suggestions=suggestions)

# Route to edit an expense
@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_expense(index):
    expenses = load_expenses()

    if request.method == 'POST':
        date = request.form.get('date')  # Use .get() to avoid KeyError
        category = request.form.get('category')
        amount = request.form.get('amount')

        if not date or not category or not amount or float(amount) <= 0:
            error_message = "Please provide valid inputs."
            return render_template('edit.html', expense=expenses[index], index=index, error=error_message)

        # Update the expense
        expenses[index] = {
            'date': date,
            'category': category,
            'amount': float(amount)
        }
        save_expenses(expenses)
        return redirect('/')

    return render_template('edit.html', expense=expenses[index], index=index)

# Route to delete an expense
@app.route('/delete/<int:index>', methods=['POST'])
def delete_expense(index):
    expenses = load_expenses()
    if 0 <= index < len(expenses):
        del expenses[index]  # Remove the expense at the specified index
        save_expenses(expenses)  # Save the updated list back to the file
    return redirect('/')

# New route for AI analysis
@app.route('/ai_analysis')
def ai_analysis():
    expenses = load_expenses()
    if not expenses:
        return jsonify({"message": "No expenses to analyze."})

    X, y = prepare_data(expenses)
    model = train_model(X, y)
    predicted_spending = predict_future_spending(model)

    insights = {
        "predicted_next_month_spending": predicted_spending[0],
        "total_spending": sum(y),
        "average_spending": np.mean(y)
    }

    return jsonify(insights)

# New route for monthly report
@app.route('/monthly_report')
def monthly_report():
    expenses = load_expenses()
    monthly_summary = {}
    
    for expense in expenses:
        date = expense['date']
        month_year = date[:7]  # Get the year and month (YYYY-MM)
        amount = expense['amount']
        
        if month_year in monthly_summary:
            monthly_summary[month_year].append(expense)
        else:
            monthly_summary[month_year] = [expense]
    
    return render_template('monthly_report.html', monthly_summary=monthly_summary)

# New route for chart data
@app.route('/chart_data')
def chart_data():
    expenses = load_expenses()
    category_totals = {}
    
    for expense in expenses:
        category = expense['category']
        amount = expense['amount']
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    return jsonify(category_totals)

if __name__ == '__main__':
    app.run(debug=True)