def predict_future_expense(current_amount):
    """
    Simple prediction logic for now:
    Predict next month expense as +20%
    Later we replace with real ML model
    """

    predicted_value = float(current_amount) * 1.20
    return round(predicted_value, 2)