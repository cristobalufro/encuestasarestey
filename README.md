# Kobo Data Export Codification

This project contains the data from a Kobo survey and the necessary files to codify the categorical variables.

## Files

### `kobo_data_export.json`

This is the original data exported from Kobo. It contains the raw data from the surveys, with the answers in text format.

### `codebook.json`

This file contains the codebook for the categorical variables in the survey. It defines the numeric codes for each category of the questions with categorical answers. It also includes the combinations for the multi-select questions.

### `kobo_data_export_coded.json`

This file is the result of applying the codebook to the original data. It contains the same data as `kobo_data_export.json`, but with the categorical answers replaced by their corresponding numeric codes from `codebook.json`. This file is ready to be used for data analysis.