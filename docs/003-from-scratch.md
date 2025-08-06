# Creating a Wrapper From Scratch

WIP!

## Architecture Overview

At a high level, a model in **pd4castr** can be any code executing inside a docker container that can read input data, and uploads output data. **pd4castr** provides a straight forward way of exposing input data and facilitating uploading output via [AWS S3 signed URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html). What this looks like in practice:

- URLs that map to model input data are exposed to the Docker container via environment variables, in the format of `INPUT_<VARIABLE_NAME>_URL` ex. `INPUT_PREDISPATCH_PRICE_URL`
  - These URLs can be fetched via standard HTTP GET requests
- An output upload URL is exposed to the docker container via the `OUTPUT_URL` environment variable
  - This can be uploaded to via a standard HTTP PUT request
  - The expected output format is ... (TODO: JSON? structure? required columns? is this where the docs should live?)

## Scaffolding Your Project

To get started, we recommend using our CLI tool to initialize your project. This guide will assume you select the `python-barebones` template.

```sh
pd4castr init
```

## Verify the Barebones Model Works

<!-- TODO -->

```sh
pdrcastr test
```

## Fetching Input Sources

<!-- TODO -->

## Integrating Your Model

<!-- TODO -->

## Uploading Output

<!-- TODO: should be the only thing handled in barebones, but maybe comments around improving it? need to review once example exists>

## Testing The Model
