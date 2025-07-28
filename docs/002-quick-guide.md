# Quick Guide

> **NOTE!** The quick guide expects you have all the [prequisites](./001-prerequisites.md) installed in your environment.

## Environment

You can verify the status of all the expected dependencies in your environment by running:

```sh
$ pd4castr check
```

## Project Setup

To get up and running with your own **pd4castr** model, begin by running the `init` command and following the prompts. To follow the quick guide, select the `python-demo` template.

```sh
$ pd4castr init
```

## Verify the Model Runs

This Python demo model is configured by default to load from 3 input sources, as seen in the [test_data/](../examples/python-demo/test_data/) directory and the [`load_input_data`](../examples/python-demo/python_demo/load_input_data.py) function:

1. `predispatch_price`
2. `predispatch_region_sum`
3. `dispatch_price`

We can test those inputs by pointing the CLI at the test data directory like:

```sh
$ pd4castr test --input-data=./test_data
```

## Adjusting the Input Sources

If you are using your own input sources for your model, you'll need to adjust them in the [`load_input_data`](../examples/python-demo/python_demo/load_input_data.py) function like so:

```py
# before
pd_price_url = os.getenv('INPUT_PREDISPATCH_PRICE_URL')
pd_regionsum_url = os.getenv('INPUT_PREDISPATCH_REGION_SUM_URL')
dp_url = os.getenv('INPUT_DISPATCH_PRICE_URL')

pd_price_json = requests.get(pd_price_url).json()
pd_regionsum_json = requests.get(pd_regionsum_url).json()
dp_json = requests.get(dp_url).json()

# after - your input source data
first_input_url = os.getenv('INPUT_FIRST_INPUT_URL')
second_input_url = os.getenv('INPUT_SECOND_INPUT_URL')

first_input = requests.get(first_input_url).json()
second_input = requests.get(second_input_url).json()
```

## Using your own Model

To use your own model, you'll need to replace the demo model code and wire it to the input & output to suit your needs. In the Python demo, we generate mock data in [run_model](../examples/python-demo/python_demo/run_model.py) - in the real world, this would be replaced with your custom code to massage the input data as needed, load and execute your model, then massage the output to the final format:

```py
# before - using mock data
results = generate_mock_output()

# after (pseudo code) - massage data, load your model, process as needed
features = generate_features(first_input, second_input)

model = your_model_library.SomeModel(...)
model.load_model('./your_model.ext')

model_results = model.predict(features)

results = process_model_results(model_results)
```

## Verifying the Output

As above, we can use the CLI to run the model and verify everything works. Once all tests have passed, the CLI will provide you a path to the output data for you to inspect.

```sh
$ pd4castr test --input-data=./test_data
```
