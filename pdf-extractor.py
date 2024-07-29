import os
import sys
import pandas as pd
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfString
import subprocess
import tempfile

def get_file_path(prompt):
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        file_path = input(f"{prompt}: ")
        return file_path

def get_form_fields(pdf):
    fields_data = {}
    if '/AcroForm' in pdf.Root:
        form = pdf.Root.AcroForm
        if '/Fields' in form:
            fields = form.Fields
            for field in fields:
                field_name = field.T[1:-1]  # Remove the parentheses around the field name
                fields_data[field_name] = field_name
    return fields_data

def prompt_user_to_edit_fields(fields_data):
    print("\nCurrent form fields:")
    fields_list = list(fields_data.keys())
    for i, field in enumerate(fields_list, start=1):
        print(f"{i}. {field}")
    
    while True:
        user_input = input("\nEnter the number of the field to correct (or 'done' to finish): ")
        if user_input.lower() == 'done':
            break
        
        try:
            field_index = int(user_input) - 1
            if 0 <= field_index < len(fields_list):
                current_field = fields_list[field_index]
                new_name = input(f"Enter new name for field '{current_field}': ")
                fields_data[current_field] = new_name
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Invalid input. Enter a number or 'done'.")

    return fields_data

def main():
    template_path = get_file_path("Enter the path to the PDF form")
    if not template_path or not os.path.isfile(template_path):
        print("No valid file selected. Exiting...")
        return

    output_dir = 'output_files'
    os.makedirs(output_dir, exist_ok=True)
    output_csv_path = os.path.join(output_dir, 'form_fields.csv')

    # Read the template PDF
    try:
        template_pdf = PdfReader(template_path)
    except Exception as e:
        print(f"Failed to read PDF file: {e}")
        return

    # Get form fields
    fields_data = get_form_fields(template_pdf)

    if not fields_data:
        print("No form fields found in the PDF.")
        return

    # Print form fields to console
    print("Extracted form fields:")
    for field in fields_data.keys():
        print(field)

    # Save to CSV
    df = pd.DataFrame([fields_data])
    df.to_csv(output_csv_path, index=False)

    print(f'Form fields have been saved to {output_csv_path}')

    # Create a temporary CSV with the header data as the fields
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_csv:
        df.to_csv(temp_csv.name, index=False)
        temp_csv_path = temp_csv.name

    # Define the output path for the filled PDF
    output_pdf_path = os.path.join(output_dir, 'filled_form.pdf')

    # Run the pdf-filler.py script with the temporary CSV
    try:
        subprocess.run([sys.executable, 'pdf-filler.py', '--pdf', template_path, '--csv', temp_csv_path])
    except Exception as e:
        print(f"Failed to run pdf-filler.py: {e}")

    # Open the filled PDF
    try:
        if sys.platform == "win32":
            os.startfile(output_pdf_path)
        elif sys.platform == "darwin":
            subprocess.run(['open', output_pdf_path])
        else:
            subprocess.run(['xdg-open', output_pdf_path])
    except Exception as e:
        print(f"Failed to open PDF file: {e}")

    # Delete the temporary CSV file
    try:
        os.remove(temp_csv_path)
        print(f"Temporary CSV file {temp_csv_path} deleted.")
    except Exception as e:
        print(f"Failed to delete temporary CSV file: {e}")

    while True:
        # Prompt user to edit fields if necessary
        corrected_fields_data = prompt_user_to_edit_fields(fields_data)

        # Save the corrected fields to a new CSV
        corrected_output_csv_path = os.path.join(output_dir, 'corrected_form_fields.csv')
        pd.DataFrame([corrected_fields_data]).to_csv(corrected_output_csv_path, index=False)
        print(f'Corrected form fields have been saved to {corrected_output_csv_path}')

        # Show diff between original and corrected CSV
        print("\nDifferences between original and corrected CSV:")
        subprocess.run(['diff', output_csv_path, corrected_output_csv_path])

        # Ask user if they want to finalize or continue editing
        finalize = input("Do you want to finalize the corrected CSV? (yes/no): ").lower()
        if finalize == 'yes':
            break

    # Update PDF with corrected field names
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                field_name = annotation['/T'][1:-1]
                if field_name in corrected_fields_data:
                    annotation.update(PdfDict(T=PdfString.encode(corrected_fields_data[field_name])))

    # Save the corrected PDF
    corrected_output_pdf_path = os.path.join(output_dir, 'corrected_form.pdf')
    PdfWriter().write(corrected_output_pdf_path, template_pdf)
    print(f'Corrected PDF has been saved to {corrected_output_pdf_path}')

    # Open the corrected PDF
    try:
        if sys.platform == "win32":
            os.startfile(corrected_output_pdf_path)
        elif sys.platform == "darwin":
            subprocess.run(['open', corrected_output_pdf_path])
        else:
            subprocess.run(['xdg-open', corrected_output_pdf_path])
    except Exception as e:
        print(f"Failed to open corrected PDF file: {e}")

if __name__ == "__main__":
    main()
