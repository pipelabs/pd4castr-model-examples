from load_input_data import load_input_data
from run_model import run_model
from upload_output_data import upload_output_data

def main():
    """
    Main orchestrator function that coordinates the entire model pipeline.
    """

    print("Starting model pipeline...")

    # Step 1: Load input data
    input_data = load_input_data()

    # Step 2: Run the model
    results = run_model(input_data)

    # Step 3: Upload output data
    upload_output_data(results)

    print("Model pipeline completed successfully!")


if __name__ == "__main__":
    main()