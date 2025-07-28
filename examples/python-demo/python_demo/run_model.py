import numpy as np
from datetime import datetime, timedelta


def run_model(pd_price_json, pd_regionsum_json, dp_json):
    """
    Generate mock output data. This is a placeholder for your model.

    Args:
        pd_price_json: Predispatch price data (ignored for mock)
        pd_regionsum_json: Predispatch region sum data (ignored for mock)
        dp_json: Dispatch price data (ignored for mock)

    Returns:
        list: List of dictionaries containing forecast data
    """

    # Generate mock output
    print("Generating mock output data...")
    results = generate_mock_output()

    print(f"Generated mock output with {len(results)} data points")
    return results


def generate_mock_output():
    """
    Generate mock output data.

    Returns:
        list: List of dictionaries containing forecast data
    """
    output = []
    states = ['VIC1', 'NSW1', 'QLD1', 'SA1', 'TAS1']

    # Initialize starting values for each state between -1000 and 16600
    current_values = {}
    for state in states:
        current_values[state] = np.random.randint(-1000, 16600)

    # Generate 48 hours of forecasts at 30 minute intervals
    start_date = datetime.now()
    for i in range(96):  # 96 intervals of 30 minutes = 48 hours
        forecast_date = start_date + timedelta(minutes=i * 30)

        data_point = {
            'forecast_datetime': forecast_date.isoformat(),
        }

        # Update values for each state with small random changes
        for state in states:
            # Generate change between -250 and 250 (smaller changes for 30min intervals)
            change = (np.random.rand() - 0.5) * 500

            # Update value ensuring it stays within bounds
            current_values[state] += change
            current_values[state] = np.clip(current_values[state], -1000, 16600)

            data_point[state] = round(current_values[state])

        output.append(data_point)

    return output
