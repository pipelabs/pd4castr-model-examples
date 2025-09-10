# Quick Guide

_Last Updated: 10th Sept. '25_

> **NOTE!** The quick guide expects you have all the
> [prerequisites](./001-prerequisites.md) installed in your environment.

- [Log in to pd4castr](#log-in-to-pd4castr)
- [Project Setup](#project-setup)
- [Verify the Model Runs](#verify-the-model-runs)
- [Adjusting the Input Sources](#adjusting-the-input-sources)
- [Using Your Own Model](#using-your-own-model)
- [Publishing Your Model](#publishing-your-model)

## Log in to pd4castr

To create a model you need to be logged in to the pd4castr CLI. You can login by
simply running:

```bash
pd4castr login
```

## Project Setup

To get up and running with your own pd4castr model, begin by running the `init`
command and following the prompts. To follow the quick guide, select the
`python-demo` template.

```bash
pd4castr init
```

## Verify the Model Runs

The Python demo model is configured to load from 3 input sources:

1. `example_static_input`
2. `predispatch_price`
3. `predispatch_region_sum`
4. `dispatch_price`

These inputs are defined and handled in 3 key places:

- inputs are defined in the
  [model configuration file](../examples/python-demo/.pd4castrrc.json)
- inputs with (optional) data fetchers include their SQL queries in the
  [/queries folder](../examples/python-demo/queries/)
- each input is loaded in the model runner script in the the
  [`load_input_data`](../examples/python-demo/python_demo/load_input_data.py)
  function

We can test these inputs using the pd4castr CLI.

Start by runnning `fetch` to run our input's data fetcher queries. This will
generate a set of test data, output to the `test_data/` directory.

```bash
pd4castr fetch
```

Then run the `test` command which will build your model image and run it,
verifying each input is accessed and output is successfully handled

```bash
pd4castr test
```

## Adjusting the Input Sources

If you are using your own input sources for your model, you'll need to adjust
them in the 3 key places outlined above.

To start, let's define a new input in our `.pd4castrrc.json` file:

```jsonc
{
  // ... the rest of the configuration
  "inputs": [
    {
      "key": "test_input",
      "trigger": "WAIT_FOR_LATEST_FILE",
      "inputSource": "0bdfd52b-efaa-455e-9a3b-1a6d2b879b73",
      "uploadFileFormat": "json",
      "targetFileFormat": "json",
      "dataFetcher": {
        "type": "AEMO_MMS",
        "checkInterval": 300,
        "config": {
          "checkQuery": "queries/test_input_check.sql",
          "fetchQuery": "queries/test_input_fetch.sql",
        },
      },
    },
    // ... other inputs here
  ],
}
```

Then create some dummy SQL queries for our data fetcher:

```sql
-- /queries/test_input_check.sql
SELECT CURRENT_TIMESTAMP;

-- /queries/test_input_fetch.sql
SELECT *
FROM (VALUES (1), (2), (3))
AS A (TEST_VALUE)
```

Then update our model runner `load_input_data` function:

```py
test_input_url = os.getenv('INPUT_TEST_INPUT_URL')

test_input = requests.get(test_input_url).json()
```

Then fetch your new input's test data and verify it works:

```bash
pd4castr fetch
pd4castr test
```

## Using Your Own Model

To use your own model, you'll need to replace the demo model code and wire it to
the input & output to suit your needs. In the Python demo, we generate mock data
in [run_model](../examples/python-demo/python_demo/run_model.py) - in the real
world, this would be replaced with your custom code to massage the input data as
needed, load and execute your model, then massage the output to the final
format:

```py
# before - using mock data
results = generate_mock_output()
```

```py
# after (pseudo code) - massage data, load your model, process as needed
features = generate_features(first_input, second_input)

model = your_model_library.SomeModel(...)
model.load_model('./your_model.ext')

model_results = model.predict(features)

results = process_model_results(model_results)
```

To verify that your model is integrated correctly and output is being generated
as expected, you can against run the `test` command to build and run your model
image:

```bash
pd4castr test
```

Output data will be saved to `test_output/` directory so you can inspect it.

[Click here](./003-technical-guide.md#model-output-format) for more information
on how to structure your output data.

## Publishing Your Model

To publish your model to the pd4castr platform, you can run the `publish`
command which will guide you through creating the new model, or updating an
existing one.

```bash
pd4castr publish
```
