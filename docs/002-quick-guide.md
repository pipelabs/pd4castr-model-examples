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

This Python demo model is configured by default to load from 3 input sources:

1. `predispatch_price`
2. `predispatch_region_sum`
3. `dispatch_price`

Which we can test like:

```sh
$ pd4castr test \
    --input=predispatch_price \
    --input=predispatch_region_sum \
    --input=dispatch_price
```

## Adjusting the Input Sources

If you are using your own input sources for your model, you'll need to adjust them in the `loadInputSources` module like so:

```py
# before
# TODO

# after
# TODO
```

## Using your own Model

To use your own model, you'll need to replace the demo model code and wire it to the input & output to suit your needs. For example, to replace the existing CBM model with a new CBM model using the example input sources we added above:

```py
# before
# TODO

# after
# TODO
```

## Verifying the Output

As above, we can use the CLI to run the model and verify everything works. Once all tests have passed, the CLI will provide you a path to the output data for you to inspect.

```sh
$ pd4castr test \
  --input=new_input_source \
  --input=TODO \
```
