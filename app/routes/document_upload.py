from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import PyPDF2
from werkzeug.utils import secure_filename
from app.utils.session_manager import get_brand_parameters, get_input_methods, update_input_method
from app.utils.text_analyzer import update_brand_parameters as update_params_from_analysis

document_upload_bp = Blueprint('document_upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        return file.read()

@document_upload_bp.route('/document-upload', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'document' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        files = [request.files['document']]

        # If user does not select file, browser also
        # submit an empty part without filename
        if not files or files[0].filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        all_text = ""

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Extract text based on file type
                if filename.endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                elif filename.endswith('.txt'):
                    text = extract_text_from_txt(file_path)
                else:
                    text = ""

                all_text += text + "\n\n"

                # Remove the file after processing
                os.remove(file_path)
            else:
                flash(f'File {file.filename} has an invalid format. Only PDF and TXT files are allowed.', 'warning')

        if all_text:
            # Analyze the text
            # Check if API integration is enabled
            from flask import session
            if not session.get('api_settings', {}).get('integration_enabled', False) or not session.get('api_settings', {}).get('api_key'):
                flash('API integration is required for text analysis. Please configure API settings.', 'danger')
                return redirect(url_for('api_settings'))

            # Import the text analyzer with API support
            from app.utils.text_analyzer import analyze_text as api_analyze_text

            try:
                print(f"Using {session['api_settings']['api_provider']} API for document analysis")
                analysis_results = api_analyze_text(all_text)
            except Exception as e:
                flash(f'API analysis failed: {str(e)}', 'danger')
                return redirect(url_for('api_settings'))

            # Update brand parameters
            brand_parameters = get_brand_parameters()
            updated_parameters = update_params_from_analysis(brand_parameters, analysis_results)

            # Use the session manager function to merge with method name
            from app.utils.session_manager import update_brand_parameters as update_session_parameters
            update_session_parameters(updated_parameters, method_name="document_upload")

            # Mark document upload as used
            update_input_method('document_upload', True, analysis_results)

            flash('Documents analyzed successfully!', 'success')
            return redirect(url_for('document_upload.results'))
        else:
            flash('Could not extract text from the uploaded files.', 'danger')

    return render_template('document_upload.html')

@document_upload_bp.route('/document-upload/results')
def results():
    # Get input methods status
    input_methods = get_input_methods()

    # Check if document upload has been used
    if not input_methods['document_upload']['used']:
        flash('Please upload and analyze documents first.', 'warning')
        return redirect(url_for('document_upload.index'))

    # Redirect to the main results page
    return redirect(url_for('results'))
