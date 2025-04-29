import csv
import re
import argparse
import sys
import os

# Regex to find potential email patterns within a string
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Define a function to validate email addresses more strictly after extraction
def is_valid_email_format(email):
    """
    Validates the format of a potential email string.
    Uses a stricter regex and checks for disallowed characters.
    """
    strict_email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if ".." in email or email.startswith('.') or email.endswith('.'):
        return False
    if "@." in email or ".@" in email:
        return False
    # Basic check for common invalid TLD patterns (e.g., ending in . or number)
    if not re.search(r'\.[a-zA-Z]{2,}$', email):
        return False
    return re.match(strict_email_regex, email) is not None

def clean_name_part(part):
    """Cleans a name part: lowercase and remove non-alphabetic chars."""
    # Keep only alphabetic characters and convert to lowercase
    cleaned = re.sub(r'[^a-z]', '', part.lower())
    return cleaned

def process_records(text, domain):
    """
    Extracts or generates, validates, and deduplicates email addresses
    from a single string containing semicolon-separated records.
    Generates an email if none is found in a record.
    """
    processed_emails = set()
    records = text.split(';')

    for record in records:
        record = record.strip()
        if not record:
            continue

        # Attempt to find existing valid emails
        potential_emails = re.findall(EMAIL_REGEX, record)
        found_valid_emails = {email for email in potential_emails if is_valid_email_format(email)}

        if found_valid_emails:
            # Add all found valid emails
            processed_emails.update(found_valid_emails)
        else:
            # No valid email found, attempt to generate one
            # Basic cleaning: remove content within brackets/parentheses
            cleaned_record = re.sub(r'\(.*?\)|<.*?>', '', record).strip()
            # Split into parts based on spaces or commas, filter empty
            parts = [p for p in re.split(r'[ ,]+', cleaned_record) if p]

            if len(parts) >= 2:
                # Assume first part is last name, second part is first name
                # This handles "LastName, FirstName" or "LastName FirstName"
                last_name = clean_name_part(parts[0])
                first_name = clean_name_part(parts[1])

                if first_name and last_name:
                    generated_email = f"{first_name}.{last_name}@{domain}"
                    # Optional: Validate the generated email format itself
                    if is_valid_email_format(generated_email):
                         processed_emails.add(generated_email)
                    # else: print(f"Warning: Could not generate valid email for record: {record}", file=sys.stderr) # Optional warning
            # else: print(f"Warning: Could not parse names from record: {record}", file=sys.stderr) # Optional warning

    return processed_emails

def write_emails_to_csv(emails, output_path):
    """Writes a set of emails to a CSV file, one email per row."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Email']) # Write header row
            for email in sorted(list(emails)): # Sort for consistent output
                writer.writerow([email])
        print(f"Successfully wrote {len(emails)} unique emails (found or generated) to {output_path}")
    except IOError as e:
        print(f"Error writing to output file {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to parse arguments and orchestrate the process."""
    parser = argparse.ArgumentParser(description="Extract or generate valid email addresses from a text file containing semicolon-separated records.")
    parser.add_argument("input_file", help="Path to the input text file (e.g., raw_text.txt)")
    parser.add_argument("output_file", help="Path to the output CSV file (e.g., generated_emails.csv)")
    parser.add_argument("--domain", required=True, help="Domain name to use for generating emails (e.g., example.com)")

    args = parser.parse_args()

    input_path = args.input_file
    output_path = args.output_file
    domain = args.domain

    # Validate domain format (basic check)
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
        print(f"Error: Invalid domain format provided: {domain}", file=sys.stderr)
        sys.exit(1)

    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}", file=sys.stderr)
        sys.exit(1)

    # Read the input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except IOError as e:
        print(f"Error reading input file {input_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Process records: extract or generate emails
    final_emails = process_records(raw_text, domain)

    # Write emails to output CSV
    write_emails_to_csv(final_emails, output_path)

if __name__ == "__main__":
    main()
