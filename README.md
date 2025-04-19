# Garbage Checker Web

## Overview
The Garbage Checker Web project is a web application designed to analyze PDF files for garbled text using advanced text analysis techniques. It provides a user-friendly interface for users to upload PDF files and configure settings for the analysis.

## Project Structure
```
garbage-checker-web
├── garbage_checker
│   ├── __init__.py
│   ├── checker.py
│   ├── config.py
│   └── routes.py
├── templates
│   └── index.html
├── static
│   └── style.css
├── app.py
├── requirements.txt
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd garbage-checker-web
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
The configuration options for the garbage checker can be found in `garbage_checker/config.py`. You can adjust the thresholds for text entropy and garbled text detection according to your needs.

## Usage
1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Use the interface to upload PDF files and configure the settings for the analysis.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.