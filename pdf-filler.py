import os
import sys
import pandas as pd
import argparse
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfString, PdfObject
from tkinter import Tk, filedialog
import pdfplumber

def get_file_path(prompt):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=prompt, filetypes=[("PDF files", "*.pdf"), ("CSV files", "*.csv")])
    return file_path

def get_font_properties(template_path):
    font_properties = {}
    with pdfplumber.open(template_path) as pdf:
        for page in pdf.pages:
            if page.annots:
                for field in page.annots:
                    if 'T' in field and 'DA' in field:
                        field_name = field['T'][1:-1]
                        font_properties[field_name] = field['DA']
    return font_properties

def fill_pdf(template_path, data, output_path, font_properties):
    # Read the template PDF
    template_pdf = PdfReader(template_path)
    template_pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))

    # Fill the form
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                field_name = annotation['/T'][1:-1]  # Remove the parentheses around the field name
                if field_name in data.index:
                    value = str(data[field_name])
                    if value and value.lower() != 'nan':
                        annotation.update(
                            PdfDict(V=PdfString.encode(value))
                        )
                        # Apply the same font properties if available
                        if field_name in font_properties:
                            annotation.update(
                                PdfDict(
                                    DA=PdfString.encode(font_properties[field_name])
                                )
                            )

    # Write the filled PDF to a file
    PdfWriter().write(output_path, template_pdf)
    print(f'Filled PDF has been saved to {output_path}')

def get_output_filename(row, columns):
    parts = [str(row[col]).replace('/', '-').replace(' ', '_') for col in columns]
    filename = "-".join(parts) + ".pdf"
    return filename

def main():
    parser = argparse.ArgumentParser(description='Fill a PDF form with data from a CSV file.')
    parser.add_argument('--pdf', type=str, help='Path to the PDF form')
    parser.add_argument('--csv', type=str, help='Path to the CSV file with data')
    args = parser.parse_args()

    if args.pdf and args.csv:
        template_path = args.pdf
        data_path = args.csv
    else:
        template_path = get_file_path("Select the PDF form")
        data_path = get_file_path("Select the CSV file with data")

    if not template_path or not data_path:
        print("File selection cancelled. Exiting...")
        return

    output_dir = 'output_files'
    os.makedirs(output_dir, exist_ok=True)

    data = pd.read_csv(data_path)
    if data.empty:
        print("No data found in CSV.")
        return

    columns = list(data.columns)
    selected_columns = []

    print("Available columns for file naming:")
    for idx, column in enumerate(columns, start=1):
        print(f"{idx}. {column}")

    while True:
        selected = input("Enter the numbers of the columns to include in the file name (comma or space-separated, or 'done' to finish): ")
        if selected.lower() == 'done':
            break
        try:
            selected_indices = [int(s.strip()) - 1 for s in selected.replace(',', ' ').split()]
            for idx in selected_indices:
                if 0 <= idx < len(columns):
                    selected_columns.append(columns[idx])
                else:
                    print(f"Invalid number: {idx + 1}. Try again.")
            break
        except ValueError:
            print("Invalid input. Enter numbers separated by commas or spaces, or 'done'.")

    if not selected_columns:
        print("No columns selected for file naming. Exiting...")
        return

    font_properties = get_font_properties(template_path)

    for index, row in data.iterrows():
        filename = get_output_filename(row, selected_columns)
        output_pdf_path = os.path.join(output_dir, filename)
        fill_pdf(template_path, row, output_pdf_path, font_properties)

if __name__ == "__main__":
    main()
