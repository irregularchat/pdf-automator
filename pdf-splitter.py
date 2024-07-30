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
