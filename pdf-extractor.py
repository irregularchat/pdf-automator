import os
import sys
import pandas as pd
from pdfrw import PdfReader
from tkinter import Tk, filedialog

def get_file_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF files", "*.pdf")])
        return file_path

def get_form_fields(pdf):
    fields_data = []
    if '/AcroForm' in pdf.Root:
        form = pdf.Root.AcroForm
        if '/Fields' in form:
            fields = form.Fields
            for field in fields:
                field_name = field.T[1:-1]  # Remove the parentheses around the field name
                fields_data.append({'Field name': field_name})
    return fields_data

def main():
    template_path = get_file_path()
    if not template_path:
        print("No file selected. Exiting...")
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
    for field in fields_data:
        print(field['Field name'])

    # Save to CSV
    df = pd.DataFrame(fields_data)
    df.to_csv(output_csv_path, index=False)

    print(f'Form fields have been saved to {output_csv_path}')

if __name__ == "__main__":
    main()
