import os
import sys
import pandas as pd
import argparse
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfString, PdfObject
from tkinter import Tk, filedialog

def get_file_path(prompt):
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=prompt, filetypes=[("PDF files", "*.pdf"), ("CSV files", "*.csv")])
    return file_path

def fill_pdf(template_path, data_path, output_path):
    # Read the template PDF
    template_pdf = PdfReader(template_path)
    template_pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))

    # Read the data from CSV
    data = pd.read_csv(data_path)
    if data.empty:
        print("No data found in CSV.")
        return

    # Fill the form
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                field_name = annotation['/T'][1:-1]  # Remove the parentheses around the field name
                if field_name in data.columns:
                    annotation.update(
                        PdfDict(V=PdfString.encode(str(data[field_name].values[0])))
                    )

    # Write the filled PDF to a file
    PdfWriter().write(output_path, template_pdf)
    print(f'Filled PDF has been saved to {output_path}')

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
    output_pdf_path = os.path.join(output_dir, 'filled_form.pdf')

    fill_pdf(template_path, data_path, output_pdf_path)

if __name__ == "__main__":
    main()
