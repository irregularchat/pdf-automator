pdf-extractor.py
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

        # Save the corrected fields to a new CSV with only headers
        corrected_output_csv_path = os.path.join(output_dir, 'corrected_form_fields.csv')
        corrected_df = pd.DataFrame(columns=corrected_fields_data.values())
        corrected_df.to_csv(corrected_output_csv_path, index=False)
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

----
pdf-filler.py
import os
import sys
import pandas as pd
import argparse
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfString, PdfObject
from tkinter import Tk, filedialog

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

----
pdf-splitter.py
import os
import sys
import pandas as pd

def get_file_path(prompt):
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        file_path = input(f"{prompt}: ")
        return file_path

def split_csv(data, output_dir):
    columns = list(data.columns)
    used_columns = set()

    while True:
        print("\nAvailable columns for splitting:")
        for idx, column in enumerate(columns, start=1):
            if column not in used_columns:
                print(f"{idx}. {column}")

        selected = input("\nEnter the numbers of the columns to include in this split (comma or space-separated, or 'done' to finish): ")
        if selected.lower() == 'done':
            break

        try:
            selected_indices = [int(s.strip()) - 1 for s in selected.replace(',', ' ').split()]
            selected_columns = [columns[idx] for idx in selected_indices if 0 <= idx < len(columns) and columns[idx] not in used_columns]
            if not selected_columns:
                print("No valid columns selected. Try again.")
                continue

            file_name = input("Enter the name for this split CSV file (without extension): ")
            split_data = data[selected_columns]
            output_csv_path = os.path.join(output_dir, f"{file_name}.csv")
            split_data.to_csv(output_csv_path, index=False)
            print(f'Split CSV file saved to {output_csv_path}')

            used_columns.update(selected_columns)
        except ValueError:
            print("Invalid input. Enter numbers separated by commas or spaces, or 'done'.")

        if used_columns == set(columns):
            print("All columns have been used.")
            break

def main():
    csv_path = get_file_path("Enter the path to the CSV file")
    if not csv_path or not os.path.isfile(csv_path):
        print("No valid file selected. Exiting...")
        return

    output_dir = 'split_csv_files'
    os.makedirs(output_dir, exist_ok=True)

    data = pd.read_csv(csv_path)
    if data.empty:
        print("No data found in CSV.")
        return

    split_csv(data, output_dir)

if __name__ == "__main__":
    main()

----
