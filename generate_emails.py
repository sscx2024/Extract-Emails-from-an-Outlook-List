import csv
import re
import argparse
import sys
import os

# Regex to find potential email patterns within a string
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
# Regex to identify list titles (e.g., "REITS:")
LIST_TITLE_REGEX = r'^\s*([\w\s]+):\s*$'

# Define a function to validate email addresses more strictly after extraction
def is_valid_email_format(email):
    """
    Validates the format of a potential email string.
    Uses a stricter regex and checks for disallowed characters.
    """
    strict_email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email: # Handle empty strings
        return False
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
    Parses text containing list titles and records, extracts or generates
    email addresses for each record, associating them with their list title.
    Returns a list of unique (list_title, email) tuples.
    """
    processed_list_emails = set() # Use a set to store (list_title, email) tuples for deduplication
    current_list_title = "Unknown" # Default list title if none found before records
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if the line is a list title
        title_match = re.match(LIST_TITLE_REGEX, line)
        if title_match:
            current_list_title = title_match.group(1).strip()
            continue # Move to the next line after finding a title

        # --- Process Record Line ---
        record = line
        # Remove trailing semicolons often found in pasted lists
        if record.endswith(';'):
            record = record[:-1].strip()

        # Attempt to find existing valid emails in the record
        potential_emails = re.findall(EMAIL_REGEX, record)
        found_valid_emails = {email for email in potential_emails if is_valid_email_format(email)}

        if found_valid_emails:
            # Add all found valid emails associated with the current list
            for email in found_valid_emails:
                processed_list_emails.add((current_list_title, email))
        else:
            # No valid email found, attempt to generate one
            # Basic cleaning: remove content within brackets/parentheses/angle brackets
            # Also remove any found (but invalid) email patterns to avoid using them as names
            cleaned_record = re.sub(EMAIL_REGEX, '', record) # Remove email-like patterns first
            cleaned_record = re.sub(r'\(.*?\)|<.*?>|\[.*?\]', '', cleaned_record).strip()
            # Split into parts based on spaces or hyphens, filter empty
            parts = [p for p in re.split(r'[\s-]+', cleaned_record) if p and p.lower() not in ['-', '–']] # Filter out stray hyphens

            if len(parts) >= 2:
                # Try common patterns: "First Last", "Last, First"
                # Simple approach: assume first part is first name, last part is last name
                # This might need refinement based on actual name formats encountered
                first_name_part = parts[0]
                last_name_part = parts[-1] # Use the last part as last name

                # Handle potential "Lastname, Firstname" by checking for comma
                if ',' in first_name_part:
                     name_parts = first_name_part.split(',', 1)
                     if len(name_parts) == 2:
                         last_name_part = name_parts[0]
                         first_name_part = name_parts[1]

                first_name = clean_name_part(first_name_part)
                last_name = clean_name_part(last_name_part)


                if first_name and last_name:
                    generated_email = f"{first_name}.{last_name}@{domain}"
                    # Validate the generated email format itself
                    if is_valid_email_format(generated_email):
                         processed_list_emails.add((current_list_title, generated_email))
                    # else: print(f"Warning: Could not generate valid email for record: {record} under list '{current_list_title}'", file=sys.stderr) # Optional warning
            # else: print(f"Warning: Could not parse names from record: {record} under list '{current_list_title}'", file=sys.stderr) # Optional warning

    # Convert set of tuples back to a list for consistent ordering if needed later
    return list(processed_list_emails)

def write_emails_to_csv(list_emails, output_path):
    """Writes a list of (list_title, email) tuples to a CSV file."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['List', 'Email']) # Write header row
            # Sort by list title, then email for consistent output
            for list_title, email in sorted(list_emails):
                writer.writerow([list_title, email])
        print(f"Successfully wrote {len(list_emails)} unique list-email pairs to {output_path}")
    except IOError as e:
        print(f"Error writing to output file {output_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while writing {output_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to parse arguments and orchestrate the process."""
    parser = argparse.ArgumentParser(description="Extract or generate valid email addresses from a text file containing lists with titles.")
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

    # Process records: extract or generate emails, associating with lists
    final_list_emails = process_records(raw_text, domain)

    # Write list-email pairs to output CSV
    write_emails_to_csv(final_list_emails, output_path)

if __name__ == "__main__":
    main()
