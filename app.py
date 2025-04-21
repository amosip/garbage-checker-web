from flask import Flask, render_template, request
from garbage_checker.config import Config
import os
import shutil # Import shutil for moving files
from werkzeug.utils import secure_filename
from garbage_checker.checker import scan_pdf_for_garbled_ocr 

app = Flask(__name__)
app.config.from_object(Config) 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Use getlist to handle multiple files from directory upload
        uploaded_files = request.files.getlist('pdf_files') 
        
        if not uploaded_files or uploaded_files[0].filename == '':
             # Check if the list is empty or contains only an empty entry
            error_message = "No folder or files selected. Please choose a folder containing PDF files."
            return render_template('index.html', error=error_message, result=None)
        
        # Process the list of uploaded files
        result = process_uploaded_files(uploaded_files)
        return render_template('index.html', result=result)
        
    # Initial GET request
    return render_template('index.html', result=None)

def process_uploaded_files(pdf_files):
    """
    Processes a list of uploaded FileStorage objects.
    Saves PDF files, checks them, and moves garbled ones.
    """
    upload_folder = "uploads"
    garbled_folder = os.path.join(upload_folder, "GARBLED")
    
    # Ensure both directories exist
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(garbled_folder, exist_ok=True)

    processed_count = 0
    garbled_count = 0
    errors = []

    for file_storage in pdf_files:
        # Basic check if it's likely a file meant to be uploaded
        if file_storage and file_storage.filename:
            # Sanitize the filename provided by the browser
            # Note: secure_filename might strip path info if browser sends it
            filename = secure_filename(file_storage.filename) 

            # Process only PDF files
            if filename.lower().endswith('.pdf'):
                processed_count += 1
                temp_save_path = os.path.join(upload_folder, filename)
                
                try:
                    # Save the file temporarily in the main uploads folder
                    file_storage.save(temp_save_path)
                    
                    # Check if the saved PDF is garbled
                    is_garbled = scan_pdf_for_garbled_ocr(temp_save_path)
                    
                    if is_garbled:
                        garbled_count += 1
                        # Construct new name and path
                        new_filename = "GARBLED_" + filename
                        destination_path = os.path.join(garbled_folder, new_filename)
                        
                        # Move the file to the GARBLED folder
                        shutil.move(temp_save_path, destination_path)
                        print(f"Moved garbled file: {filename} to {destination_path}")
                    # else: Keep non-garbled files in the main uploads folder for now
                        
                except Exception as e:
                    error_message = f"Error processing file '{filename}': {e}"
                    print(error_message)
                    errors.append(error_message)
                    # Clean up temp file if move failed or scan failed after save
                    if os.path.exists(temp_save_path):
                         try:
                             os.remove(temp_save_path)
                         except OSError as remove_err:
                             print(f"Error removing temp file {temp_save_path}: {remove_err}")


    # --- Prepare summary message ---
    summary = f"Processed {processed_count} PDF files. Found {garbled_count} garbled files."
    if garbled_count > 0:
        summary += f" Garbled files were moved to the '{garbled_folder}' directory."
    if errors:
        summary += "\nEncountered errors:\n" + "\n".join(errors)
        
    return summary

if __name__ == '__main__':
    app.run(debug=True)