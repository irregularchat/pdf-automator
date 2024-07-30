# PDF Automator

This project provides a set of tools for extracting, filling, and splitting PDF forms using Python. The tools allow you to work with PDF forms and CSV data to automate PDF form handling.
## Roadmap
- [x] Extract form fields from a PDF file
- [x] Split a CSV file into multiple CSV files based on selected columns
- [x] Fill a PDF form with data from one or more CSV files 
- [ ] Extract text from multiple PDF fields to a CSV file
- [ ] Web interface for uploading PDF and CSV files
- [ ] Dockerize the application
- [ ] Create MEMO from scratch using DA Pubs template and 25-50 
- [ ] Create Word Mail Merge from PDF 
- [ ] Create PDF from Word Mail Merge

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setting Up the Environment

1. **Clone the Repository**

```bash
git clone https://github.com/irregularchat/pdf-automator.git
cd pdf-automator
```

2. **Create a Virtual Environment**

```bash
python3 -m venv venv
```

3. **Activate the Virtual Environment**

   - On macOS/Linux:

```bash
source venv/bin/activate
```

   - On Windows:

```bash
venv\Scripts\activate
```

4. **Install Requirements**

```bash
pip install -r requirements.txt
```

## Scripts and Usage

### 1. PDF Extractor

Extract form fields from a PDF file.

```bash
python3 pdf-extractor.py /path/to/your/pdf_file.pdf
```

### 2. PDF Filler

Fill a PDF form with data from one or more CSV files.

```bash
python3 pdf-filler.py --pdf /path/to/your/pdf_file.pdf --csv /path/to/your/csv_file1.csv /path/to/your/csv_file2.csv
```

### 3. PDF Splitter

Split a CSV file into multiple CSV files based on selected columns.

```bash
python3 pdf-splitter.py /path/to/your/csv_file.csv
```

## Examples

### Extracting Form Fields

To extract form fields from a PDF:

```bash
python3 pdf-extractor.py /path/to/your/pdf_file.pdf
```

This will create a CSV file named `form_fields.csv` in the `output_files` directory.

### Filling a PDF Form

To fill a PDF form with data from multiple CSV files:

```bash
python3 pdf-filler.py --pdf output_files/corrected_form.pdf --csv split_csv_files/People.csv split_csv_files/School.csv split_csv_files/Unit.csv
```

You will be prompted to select rows from each CSV file and the columns to include in the file name.

### Splitting a CSV File

To split a CSV file into multiple CSV files:

```bash
python3 pdf-splitter.py /path/to/your/csv_file.csv
```

You will be prompted to select columns to include in each split CSV file and to name each split CSV file.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

### Pull Request Process
1. Fork the repository
2. Create a new branch (`git checkout -b feature` OR graphically in your git client)
3. Make changes
4. Commit your changes (`git commit -am 'Add/FIXED new feature'` OR graphically in your git client)
5. Push to the branch (`git push origin feature`)
6. Create a new Pull Request


