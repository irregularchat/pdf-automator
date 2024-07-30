import os
import sys
import pandas as pd
import argparse
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfString, PdfObject
import pdfplumber

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
    print(f"Filling PDF with data: {data.to_dict()}")
    template_pdf = PdfReader(template_path)
    template_pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))

    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                field_name = annotation['/T'][1:-1]
                if field_name in data.index:
                    value = str(data[field_name])
                    if value and value.lower() != 'nan':
                        annotation.update(
                            PdfDict(V=PdfString.encode(value))
                        )
                        if field_name in font_properties:
                            annotation.update(
                                PdfDict(
                                    DA=PdfString.encode(font_properties[field_name])
                                )
                            )
                    else:
                        annotation.update(
                            PdfDict(V=PdfString.encode(''))
                        )

    PdfWriter().write(output_path, template_pdf)
    print(f'Filled PDF has been saved to {output_path}')

def get_output_filename(row, columns):
    parts = [str(row[col]).replace('/', '-').replace(' ', '_') for col in columns if pd.notna(row[col])]
    filename = "-".join(parts) + ".pdf"
    return filename

def combine_rows(selected_data):
    combined_data = pd.DataFrame()
    for df in selected_data:
        if combined_data.empty:
            combined_data = df.copy()
        else:
            combined_data = combined_data.join(df, how='outer')
    return combined_data

def main():
    parser = argparse.ArgumentParser(description='Fill a PDF form with data from one or multiple CSV files.')
    parser.add_argument('--pdf', type=str, help='Path to the PDF form')
    parser.add_argument('--csv', type=str, nargs='*', help='Paths to the CSV files')
    args = parser.parse_args()

    if args.pdf:
        template_path = args.pdf
    else:
        print("No PDF file specified. Exiting...")
        return

    if args.csv:
        data_paths = args.csv
    else:
        print("No CSV files specified. Exiting...")
        return

    output_dir = 'output_files'
    os.makedirs(output_dir, exist_ok=True)

    data_frames = []
    for data_path in data_paths:
        data = pd.read_csv(data_path)
        if data.empty:
            print(f"No data found in CSV: {data_path}")
            continue

        print(f"\nAvailable rows in {data_path}:")
        print(data)
        selected_rows = input(f"Enter the row indices to use from {data_path} (comma or space-separated, or 'all' for all rows): ").strip()
        if selected_rows.lower() == 'all' or selected_rows == '':
            data_frames.append(data)
            print(f"Added all rows from {data_path}")
        else:
            try:
                selected_indices = [int(s.strip()) for s in selected_rows.replace(',', ' ').split()]
                selected_data = data.iloc[selected_indices]
                data_frames.append(selected_data)
                print(f"Added selected rows {selected_indices} from {data_path}")
            except ValueError:
                print(f"Invalid input for rows in {data_path}. Using all rows.")
                data_frames.append(data)

    if not data_frames:
        print("No valid data found in any CSV file. Exiting...")
        return

    combined_data = pd.concat(data_frames, axis=1)
    print(f"Combined data:\n{combined_data}")
    if combined_data.empty:
        print("Combined data is empty. Exiting...")
        return

    font_properties = get_font_properties(template_path)

    columns = list(combined_data.columns)
    selected_columns = []

    print("Available columns for file naming:")
    for idx, column in enumerate(columns, start=1):
        print(f"{idx}. {column}")

    while True:
        selected = input("Enter the numbers of the columns to include in the file name (comma or space-separated, or 'done' to finish): ").strip()
        if selected.lower() == 'done':
            break
        if selected == '':
            print("No columns selected for file naming. Exiting...")
            return
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

    for index, row in combined_data.iterrows():
        filename = get_output_filename(row, selected_columns)
        output_pdf_path = os.path.join(output_dir, filename)
        fill_pdf(template_path, row, output_pdf_path, font_properties)

if __name__ == "__main__":
    main()
