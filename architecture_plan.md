# KoboToolbox Data Parsing Architecture

This document outlines the architecture for parsing KoboToolbox form data to correctly map backend names to frontend labels.

## 1. Analysis of `assets/{ASSET_UID}.json` Structure

Based on the existing script, the JSON response from the KoboToolbox API has the following relevant structure:

```json
{
  "name": "Form Title",
  "deployment__submission_count": 123,
  "content": {
    "survey": [
      {
        "type": "begin_group",
        "name": "group_name",
        "label": ["Group Label"],
        "children": [
          {
            "type": "text",
            "name": "question_name",
            "$autoname": "question_autoname",
            "label": ["Question Label"]
          }
        ]
      }
    ],
    "choices": [
      {
        "list_name": "yes_no",
        "choices": [
          {
            "name": "yes",
            "label": ["Yes"]
          },
          {
            "name": "no",
            "label": ["No"]
          }
        ]
      }
    ]
  }
}
```

### Key Observations:

*   **`survey`**: An array of objects representing the form's questions and groups in a hierarchical structure.
*   **`choices`**: An array of objects defining the available choices for `select_one` and `select_multiple` questions.
*   **Nesting**: Groups contain a `children` array, which creates a nested structure.
*   **Labels**: Both questions and choices have a `label` field, which is an array of strings (likely for multi-language support).

## 2. Proposed Parsing Logic

The current implementation fails because it flattens the nested structure of the `survey` data, causing group names to be concatenated with question names. The new design will address this by recursively processing the `survey` array and creating precise mappings.

### Step 1: Parse Choices

First, we will parse the `choices` section to create a lookup table for answer labels.

*   **`choice_lookup` Dictionary:**
    *   **Purpose:** To map choice names (e.g., "yes") to their corresponding labels (e.g., "Yes").
    *   **Structure:** `{ "choice_name": "Choice Label" }`
    *   **Example:** `{ "yes": "Yes", "no": "No" }`

### Step 2: Parse Survey Questions

Next, we will recursively parse the `survey` section to build a mapping of question names to their labels, correctly handling groups.

*   **`name_to_label` Dictionary:**
    *   **Purpose:** To map the backend question names (e.g., "question_name") to their user-friendly labels (e.g., "Question Label").
    *   **Structure:** `{ "question_name": "Question Label" }`
    *   **Key Detail:** The keys will be the question's `name` or `$autoname`, and the values will be the first element of the `label` array. Group names will be ignored in the final mapping.

### Recursive Parsing Function (`process_survey_elements`)

This function will be redesigned to traverse the `survey` hierarchy without passing down a path context.

```python
def process_survey_elements(elements):
    for elem in elements:
        # If the element is a group, recursively process its children
        if elem.get('type') in ['begin_group', 'begin_repeat'] and 'children' in elem:
            process_survey_elements(elem['children'])

        # If the element is a question with a label, add it to the map
        name = elem.get('$autoname') or elem.get('name')
        label_list = elem.get('label')
        if name and label_list:
            name_to_label[name] = label_list[0]
```

This approach ensures that only question names are used as keys in the `name_to_label` dictionary, preventing group names from appearing in the final output.

## 3. Integration Plan

The new parsing logic will be integrated into the `fetch_form_structure` function in `run.py`. The `translate_dataframe` function will then use the generated `name_to_label` and `choice_lookup` dictionaries to produce a clean, user-friendly output that mirrors the KoboToolbox UI.