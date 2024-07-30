version: '3'
services:
  pdf-extractor:
    build: .
    volumes:
      - .:/app
    environment:
      - FILE_PATH=
    entrypoint: ["python", "pdf-extractor.py", "$FILE_PATH"]

  pdf-splitter:
    build: .
    volumes:
      - .:/app
    environment:
      - FILE_PATH=
    entrypoint: ["python", "pdf-splitter.py", "$FILE_PATH"]

  pdf-filler:
    build: .
    volumes:
      - .:/app
    environment:
      - PDF_PATH=
      - CSV_PATHS=
    entrypoint: ["python", "pdf-filler.py", "--pdf", "$PDF_PATH", "--csv", "$CSV_PATHS"]