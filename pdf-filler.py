import os
import sys
import pandas as pd
import argparse
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfString, PdfObject

def fill_pdf(template_path, data, output_path):
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
                    annotation.update(
                        PdfDict(V=PdfString.encode(value))
                    )

    PdfWriter().write(output_path, template_pdf)
    print(f'Filled PDF has been saved to {output_path}')

def get_output_filename(row, columns):
    parts = [str(row[col]).replace('/', '-').replace(' ', '_') for col in columns if pd.notna(row[col])]
    filename = "-".join(parts) + ".pdf"
    return filename

def get_data_from_csv(file_path):
    data = pd.read_csv(file_path)
    if data.empty:
        print(f"No data found in CSV: {file_path}")
        return pd.DataFrame()

    print(f"\nAvailable rows in {file_path}:")
    print(data)
    while True:
        selected_indices = input(f"Enter the row indices to use from {file_path} (comma or space-separated, or 'all' for all rows): ").strip()
        if selected_indices.lower() == 'all' or selected_indices == '':
            print(f"Added all rows from {file_path}")
            return data
        try:
            selected_indices = [int(s.strip()) for s in selected_indices.replace(',', ' ').split()]
            selected_data = data.iloc[selected_indices]
            print(f"Added selected rows {selected_indices} from {file_path}")
            return selected_data
        except ValueError:
            print(f"Invalid input for rows in {file_path}. Please enter valid indices.")

def get_selected_columns(columns):
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
            sys.exit(1)
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

    return selected_columns

def main():
    parser = argparse.ArgumentParser(description='Fill a PDF form with data from one or multiple CSV files.')
    parser.add_argument('--pdf', type=str, help='Path to the PDF form')
    parser.add_argument('--csv', type=str, nargs='*', help='Paths to the CSV files')
    args = parser.parse_args()

    if not args.pdf or not args.csv:
        root = Tk()
        root.withdraw()  # Hide the root window
        pdf_path = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF files", "*.pdf")])
        csv_paths = filedialog.askopenfilenames(title="Select CSV files", filetypes=[("CSV files", "*.csv")])
        if not pdf_path or len(csv_paths) < 2:
            print("You must select one PDF file and at least two CSV files. Exiting...")
            return
        args.pdf = pdf_path
        args.csv = csv_paths

    if len(args.csv) < 2:
        print("At least two CSV files are required. Exiting...")
        return

    output_dir = 'output_files'
    os.makedirs(output_dir, exist_ok=True)

    data_frames = []
    for data_path in args.csv:
        data = get_data_from_csv(data_path)
        if not data.empty:
            data_frames.append(data)

    if len(data_frames) < 2:
        print("Valid data from at least two CSV files is required. Exiting...")
        return

    combined_data = data_frames[0]
    for df in data_frames[1:]:
        combined_data = combined_data.merge(df.assign(key=1), how='cross').drop('key', axis=1)

    print(f"Combined data:\n{combined_data}")
    if combined_data.empty:
        print("Combined data is empty. Exiting...")
        return

    columns = list(combined_data.columns)
    selected_columns = get_selected_columns(columns)

    for index, row in combined_data.iterrows():
        filename = get_output_filename(row, selected_columns)
        output_pdf_path = os.path.join(output_dir, filename)
        fill_pdf(args.pdf, row, output_pdf_path)

if __name__ == "__main__":
    main()
