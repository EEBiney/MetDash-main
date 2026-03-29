import zipfile
import io
import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
from Python_script_test import (
    load_data,
    process_heights,
    subtract_blank,
    normalize_ribitol,
    plot_results,
    clean_data,
    export_results
)

app = Flask(__name__)

# Relative paths for UPLOAD and REPORTS
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#UPLOAD_FOLDER = os.path.join(BASE_DIR, "UPLOAD")
#REPORTS_FOLDER = os.path.join(BASE_DIR, "REPORTS")

# Ensure folders exist
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#os.makedirs(REPORTS_FOLDER, exist_ok=True)

#app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
#app.config["REPORTS_FOLDER"] = REPORTS_FOLDER

# Home page
@app.route("/")
def home():
    return render_template("MetDash_Home.html")

# About page
@app.route("/about")
def about():
    return render_template("MetDash_About.html")

# Blog page
@app.route("/blog")
def blog():
    return render_template("MetDash_Analysis1.html")

# Contact page
@app.route("/contact")
def contact():
    return render_template("MetDash_Contact.html")

# Analysis page
@app.route("/analysis")
def analysis():
    return render_template("MetDash_Analysis.html")

@app.route("/upload", methods=["POST"])
def process():
    try:
        # Expect uploaded files
        if "data" not in request.files or "sample" not in request.files:
            return jsonify({"error": "Upload both data.csv and Sample_info.txt"}), 400
    
        data_file = request.files["data"]
        sample_file = request.files["sample"]
    
        # Use the original filenames
        data_filename = secure_filename(data_file.filename)
        sample_filename = secure_filename(sample_file.filename)
    
        # Strip extension from data_filename
        base_name = os.path.splitext(data_filename)[0]
    
        # Build full paths inside UPLOAD folder
        #data_path = os.path.join(app.config["UPLOAD_FOLDER"], data_filename)
        #sample_path = os.path.join(app.config["UPLOAD_FOLDER"], sample_filename)
    
        # Save uploaded files with their original names
        #data_file.save(data_path)
        #sample_file.save(sample_path)
        
        # Read files into memory — no disk writes
        data_bytes = io.BytesIO(data_file.read())
        sample_bytes = io.BytesIO(sample_file.read())
        
        # Run pipeline
        temp, samp = load_data(data_bytes, sample_bytes)
        heights = process_heights(temp, samp)
        heights, BK = subtract_blank(heights, samp)
        heights = normalize_ribitol(heights)
    
        heights, samp = clean_data(heights, samp)
        
        #plots_path = os.path.join(REPORTS_FOLDER, f"{base_name}_plots.pdf")
        #results_path = os.path.join(REPORTS_FOLDER, f"{base_name}_results.txt")
    
        #plot_results(heights, samp, outfile=plots_path)
        #final = export_results(heights, samp, outfile=results_path)
    
        # Create ZIP bundle
        #zip_path = os.path.join(REPORTS_FOLDER, f"{base_name}_bundle.zip")
        #with zipfile.ZipFile(zip_path, "w") as zf:
            #zf.write(results_path, arcname=f"{base_name}_results.txt")
            #zf.write(plots_path, arcname=f"{base_name}_plots.pdf")
    
        # Generate outputs into memory
        plots_buffer = io.BytesIO()
        results_buffer = io.BytesIO()
    
        plot_results(heights, samp, outfile=plots_buffer)
        final = export_results(heights, samp, outfile=results_buffer)
    
        plots_buffer.seek(0)
        results_buffer.seek(0)
    
        # Build zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{base_name}_results.txt", results_buffer.read())
            zf.writestr(f"{base_name}_plots.pdf", plots_buffer.read())
        zip_buffer.seek(0)
        
        # Return ZIP file as download
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{base_name}_bundle.zip"
        )
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
