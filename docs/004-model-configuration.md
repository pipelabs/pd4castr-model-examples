# Model Configuration

Every model is configured by a `.pd4castrrc.json` file in the root directory of
your project.

We provide a [JSON schema](../schemas/v1/model-config.json) and an
[example configuration](../examples/python-demo/.pd4castrrc.json) as well as
documentation with examples below.

```jsonc
{
  /**
   * The name of your model - this will appear in the UI like `python-demo`
   */
  "name": "Python Demo",

  /**
   * The type of variables in your model output.
   *
   * Possible values:
   *
   * - "price"
   */
  "forecastVariable": "price",

  /**
   * The time horizon of your models output, used to categorize your model in the UI.
   *
   * Possible values:
   *
   * - "actual"
   * - "day_ahead"
   * - "week_ahead"
   * - "quarterly"
   */
  "timeHorizon": "day_ahead",

  /**
   * Metadata about your model. This is an arbitrary object, however some fields
   * such as `author` and `version` may be standardised in the future.
   */
  "metadata": {
    "author": "Your Company Name",
    "version": "1.0.0",
  },

  /**
   * Model inputs are defined as an array.
   *
   * Possible `uploadFileFormat` and `targetFileFormat` values:
   *
   * - "csv"
   * - "json"
   * - "parquet"
   */
  "inputs": [
    /**
     * An example input that uses static data.
     *
     * Inputs using static data will look in the `STATIC/{KEY}` path in their
     * respective input bucket (as defined by `inputSource`).
     *
     * In this example, it will look for data uploaded to the `STATIC/EXAMPLE_STATIC_DATA/`
     * path in the input bucket of ID `0bdfd52b-efaa-455e-9a3b-1a6d2b879b73`
     *
     * When the model runs, this input would be available at URL exposed via
     * `INPUT_EXAMPLE_STATIC_DATA_URL` environment variable.
     *
     * Note that unless you are regularly changing the data of your static input,
     * you most likely want to use the `USE_MOST_RECENT_FILE` trigger type so that
     * it doesn't block model execution waiting for data that doesn't change.
     */
    {
      "key": "example_static_data",
      "inputSource": "0bdfd52b-efaa-455e-9a3b-1a6d2b879b73",
      "trigger": "USE_MOST_RECENT_FILE",
      "uploadFileFormat": "json",
      "targetFileFormat": "json",
    },
    /**
     * An example input using data fetcher from the `AEMO_MMS` provider.
     *
     * Inputs using data fetchers will automatically run their `checkQuery`
     * every X seconds as defined by their `checkInterval`.
     *
     * When the result of the `checkQuery` changes, the `fetchQuery` will be
     * ran, and the result will be stored in the respective input bucket (as
     * defined by `inputSource`).
     *
     * Choosing the correct `trigger` condition here depends entirely on
     * wether you want fresh data or not; if you want to require updated data
     * from your fetchers, you most likely want these configured to
     * `WAIT_FOR_LATEST_FILE`.
     */
    {
      "key": "data_from_aemo_mms",
      "inputSource": "0bdfd52b-efaa-455e-9a3b-1a6d2b879b73",
      "trigger": "WAIT_FOR_LATEST_FILE",
      "uploadFileFormat": "json",
      "targetFileFormat": "json",
      "fetcher": {
        "type": "AEMO_MMS",
        "checkInterval": 300,
        "config": {
          "checkQuery": "queries/dispatch_price_check.sql",
          "fetchQuery": "queries/dispatch_price_fetch.sql",
        },
      },
    },
    /**
     * An example static input using file format transformation
     *
     * Although the platform primarily uses JSON, if you have input data in
     * a supported format then it can be transformed to another supported
     * format to be provided to your model.
     *
     * Note that this advanced functionality is not support by the `pd4castr` CLI
     * and may require you to bypass local model I/O checks with the `--skip-checks`
     * flag.
     *
     * In this example, your static data would be in the Parquet format, and your model
     * would expect CSV.
     */
    {
      "key": "data_requiring_transform",
      "trigger": "USE_MOST_RECENT_FILE",
      "uploadFileFormat": "parquet",
      "targetFileFormat": "csv",
    },
  ],
  /**
   * Model outputs are defined as an array.
   *
   * Supported `type` values:
   *
   * - "float"
   * - "integer"
   * - "string"
   * - "date"
   * - "boolean"
   * - "unknown"
   */
  "outputs": [
    /**
     * An example float output variable.
     *
     * As this is a numeric type, it would be rendered in the pd4castr UI.
     */
    {
      "type": "FLOATVAL",
      "type": "float",
      "seriesKey": true,
      "colour": "#84EDDC",
    },
    /**
     * An example string output variable.
     *
     * As this is not a numeric type, it would NOT be rendered in the pd4castr UI.
     */
    {
      "type": "STRINGVAL",
      "type": "string",
      "seriesKey": true,
      "colour": "#FD4E4E",
    },
  ],

  /**
   * Do not change these values - they are synchronized with the pd4castr platform
   * to ensure your local model doesn't fall out of sync with the remote model.
   */
  "// WARNING: DO NOT MODIFY THESE SYSTEM MANAGED VALUES": "",
  "$$id": null,
  "$$modelGroupID": null,
  "$$revision": 0,
  "$$dockerImage": null,
}
```
