from flask import Flask, render_template, request, redirect, url_for, Response, stream_with_context, session
from garbage_checker.config import Config
import os
import shutil 
import uuid # To generate unique task IDs
import time # For potential delays/demo
import json # To format SSE data
from werkzeug.utils import secure_filename
from garbage_checker.checker import scan_pdf_for_garbled_ocr 

app = Flask(__name__)
app.config.from_object(Config) 
# Need a secret key for session management (used to store task data temporarily)
app.secret_key = os.urandom(24) 

# --- Main Route ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('pdf_files') 
        
        if not uploaded_files or uploaded_files[0].filename == '':
            error_message = "No folder or files selected."
            return render_template('index.html', error=error_message, result=None)
        
        # Create a unique task ID and temporary folder for this request
        task_id = str(uuid.uuid4())
        temp_task_folder = os.path.join("uploads", task_id)
        os.makedirs(temp_task_folder, exist_ok=True)
        
        saved_files_info = [] # Store paths of successfully saved files for processing
        
        # Save files to the temporary task folder first
        for file_storage in uploaded_files:
            if file_storage and file_storage.filename:
                filename = secure_filename(file_storage.filename)
                if filename.lower().endswith('.pdf'):
                    save_path = os.path.join(temp_task_folder, filename)
                    try:
                        file_storage.save(save_path)
                        saved_files_info.append({"path": save_path, "original_name": filename})
                    except Exception as e:
                        print(f"Error saving {filename} for task {task_id}: {e}")
                        # Optionally: add error feedback to user later

        if not saved_files_info:
             error_message = "No valid PDF files were found or saved."
             # Clean up empty task folder
             try:
                 os.rmdir(temp_task_folder)
             except OSError:
                 pass # Ignore if already removed or not empty (shouldn't happen here)
             return render_template('index.html', error=error_message, result=None)

        # Store file list in session (simple approach, consider alternatives for large lists/production)
        session[f'task_{task_id}_files'] = saved_files_info
        
        # Redirect to the processing page
        return redirect(url_for('processing_page', task_id=task_id))
        
    # Initial GET request
    return render_template('index.html', result=None)

# --- Processing Page Route ---
@app.route('/processing/<task_id>')
def processing_page(task_id):
    # Check if task data exists (basic check)
    if f'task_{task_id}_files' not in session:
         # Handle case where task ID is invalid or session expired
         return "Error: Processing task not found or session expired.", 404
    return render_template('processing.html', task_id=task_id)

# --- SSE Stream Route ---
@app.route('/progress-stream/<task_id>')
def progress_stream(task_id):
    
    def generate_progress(task_id):
        files_to_process = session.get(f'task_{task_id}_files')
        if not files_to_process:
            yield f"data: {json.dumps({'progress': 100, 'message': 'Error: No files found for this task.'})}\n\n"
            return

        garbled_folder = os.path.join("uploads", "GARBLED")
        os.makedirs(garbled_folder, exist_ok=True)
        
        total_files = len(files_to_process)
        processed_count = 0
        garbled_count = 0

        yield f"data: {json.dumps({'progress': 0, 'message': f'Starting processing for {total_files} files...'})}\n\n"
        time.sleep(0.5) # Small delay to allow UI to update

        for i, file_info in enumerate(files_to_process):
            file_path = file_info["path"]
            original_name = file_info["original_name"]
            current_progress = int(((i + 1) / total_files) * 100)
            
            if not os.path.exists(file_path):
                 yield f"data: {json.dumps({'progress': current_progress, 'message': f'Skipping missing file: {original_name}'})}\n\n"
                 continue

            message = f"Processing ({i+1}/{total_files}): {original_name}"
            yield f"data: {json.dumps({'progress': current_progress, 'message': message})}\n\n"
            
            try:
                is_garbled = scan_pdf_for_garbled_ocr(file_path)
                
                if is_garbled:
                    garbled_count += 1
                    new_filename = "GARBLED_" + original_name
                    destination_path = os.path.join(garbled_folder, new_filename)
                    try:
                        shutil.move(file_path, destination_path)
                        # Don't yield success message here, do it at the end
                    except Exception as move_err:
                         yield f"data: {json.dumps({'progress': current_progress, 'message': f'Error moving {original_name}: {move_err}'})}\n\n"
                # else: Non-garbled files remain in the temp task folder for now
                
            except Exception as e:
                 yield f"data: {json.dumps({'progress': current_progress, 'message': f'Error checking {original_name}: {e}'})}\n\n"
            
            processed_count += 1
            # time.sleep(0.1) # Optional: slow down for demo purposes

        # --- Final Summary ---
        final_message = f"Processing complete. Processed {processed_count}/{total_files} files. Found {garbled_count} garbled files (moved to GARBLED folder)."
        yield f"data: {json.dumps({'progress': 100, 'message': final_message, 'status': 'complete'})}\n\n"

        # --- Cleanup ---
        # Remove task data from session
        session.pop(f'task_{task_id}_files', None) 
        # Remove the temporary task folder and its contents (non-garbled files)
        temp_task_folder = os.path.join("uploads", task_id)
        try:
            shutil.rmtree(temp_task_folder)
            print(f"Cleaned up temporary folder: {temp_task_folder}")
        except Exception as e:
            print(f"Error cleaning up temporary folder {temp_task_folder}: {e}")
            yield f"data: {json.dumps({'progress': 100, 'message': f'Warning: Could not clean up temporary files: {e}', 'status': 'complete'})}\n\n"


    # Return a streaming response using the generator
    return Response(stream_with_context(generate_progress(task_id)), mimetype='text/event-stream')


# Remove or comment out the old process_uploaded_files function
# def process_uploaded_files(pdf_files):
#    # ... (old code) ...

if __name__ == '__main__':
    app.run(debug=True, threaded=True) # threaded=True might be needed for concurrent SSE/requests