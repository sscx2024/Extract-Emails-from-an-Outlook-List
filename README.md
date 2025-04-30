# Email List Generator

This Python script (`generate_emails.py`) processes a text file containing lists of contacts organized under titles. It extracts existing email addresses or generates potential email addresses based on names if none are found. The output is a CSV file mapping each email address to its corresponding list title.

## Input File Format

The input text file should be structured as follows:

-   **List Titles:** Indicate the start of a new list with a line ending in a colon (e.g., `REITS:`).
-   **Contact Records:** Each line following a title represents a contact. The script expects contact information that might include names and potentially an email address within parentheses, brackets, or separated by spaces/commas.
-   **Separators:** Records within a list are typically separated by newlines. The script can handle pasted content that might use semicolons at the end of lines.
-   **Blank Lines:** Blank lines are ignored.

**Example Input (`input.txt`):**

```text
LIST ONE:

John Doe (john.doe@example.com)
Jane Smith

LIST TWO:

Peter Jones <peter.jones@sample.org>
Alice Williams - Marketing;
Bob Brown, bob.brown@sample.org
```

## Features

-   Extracts valid email addresses found within contact records.
-   Generates emails in the format `firstname.lastname@domain.com` if no valid email is found (attempts basic name parsing).
-   Associates each extracted or generated email with the most recent list title found in the input file.
-   Handles common formatting variations like parentheses `()`, angle brackets `<>`, and trailing semicolons `;`.
-   Outputs a CSV file with 'List' and 'Email' columns.
-   Deduplicates email addresses within the scope of their list title.

## Requirements

-   Python 3.x

## Usage

Run the script from your terminal:

```bash
python generate_emails.py <input_file_path> <output_csv_path> --domain <your_domain.com>
```

**Arguments:**

-   `<input_file_path>`: Path to the input text file (e.g., `raw_text.txt`).
-   `<output_csv_path>`: Path where the output CSV file will be saved (e.g., `output_emails.csv`).
-   `--domain <your_domain.com>`: **Required.** The domain name to use when generating email addresses (e.g., `company.com`).

**Example Command:**

```bash
python generate_emails.py contacts.txt generated_list.csv --domain mybusiness.com
```

This command will read `contacts.txt`, process the lists and contacts, generate emails using `@mybusiness.com` where needed, and save the results to `generated_list.csv`.

## Output CSV Format

The output CSV file will have two columns:

-   **List:** The title of the list the contact belongs to.
-   **Email:** The extracted or generated email address.

**Example Output (`generated_list.csv`):**

```csv
List,Email
LIST ONE,jane.smith@mybusiness.com
LIST ONE,john.doe@example.com
LIST TWO,alice.williams@mybusiness.com
LIST TWO,bob.brown@sample.org
LIST TWO,peter.jones@sample.org
