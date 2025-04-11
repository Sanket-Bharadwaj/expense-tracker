import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def load_expenses():
    try:
        with open('expenses.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

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

# Load expenses and prepare data
expenses = load_expenses()
X, y = prepare_data(expenses)

# Train the model
model = train_model(X, y)

# Predict future spending for the next month
predicted_spending = predict_future_spending(model)
print(f"Predicted spending for the next month: ₹{predicted_spending[0]:.2f}")