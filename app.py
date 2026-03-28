import zipfile
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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "UPLOAD")
REPORTS_FOLDER = os.path.join(BASE_DIR, "REPORTS")

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORTS_FOLDER"] = REPORTS_FOLDER

# Home page
@app.route("/home")
def home():
    return render_template("MetDash - Home.html")

# About page
@app.route("/about")
def about():
    return render_template("MetDash - About.html")

# Blog page
@app.route("/blog")
def blog():
    return render_template("MetDash - Blog.html")

# Contact page
@app.route("/contact")
def contact():
    return render_template("MetDash - Contact.html")

# Analysis page
@app.route("/analysis")
def analysis():
    return render_template("MetDash - Analysis.html")

@app.route("/upload", methods=["POST"])
def process():
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
    data_path = os.path.join(app.config["UPLOAD_FOLDER"], data_filename)
    sample_path = os.path.join(app.config["UPLOAD_FOLDER"], sample_filename)

    # Save uploaded files with their original names
    data_file.save(data_path)
    sample_file.save(sample_path)

    # Run pipeline
    temp, samp = load_data(data_path, sample_path)
    heights = process_heights(temp, samp)
    heights, BK = subtract_blank(heights, samp)
    heights = normalize_ribitol(heights)

    heights, samp = clean_data(heights, samp)
    
    plots_path = os.path.join(REPORTS_FOLDER, f"{base_name}_plots.pdf")
    results_path = os.path.join(REPORTS_FOLDER, f"{base_name}_results.txt")

    plot_results(heights, samp, outfile=plots_path)
    final = export_results(heights, samp, outfile=results_path)

    # Create ZIP bundle
    zip_path = os.path.join(REPORTS_FOLDER, f"{base_name}_bundle.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(results_path, arcname=f"{base_name}_results.txt")
        zf.write(plots_path, arcname=f"{base_name}_plots.pdf")

    # Return ZIP file as download
    return send_file(
        zip_path,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{base_name}_bundle.zip"
    )

def process2():
    #store typed input data as a variable
    input_data = request.form['inputData']

    #store option value as a variable
    option = request.form['optionSelect']

    # Expect uploaded file
    if "data" not in request.files:
        return jsonify({"error": "Upload both data.csv"}), 400

    data_file = request.files["data"]

    # Use the original filenames
    data_filename = secure_filename(data_file.filename)

    # Strip extension from data_filename
    base_name = os.path.splitext(data_filename)[0]

    # Build full paths inside UPLOAD folder
    data_path = os.path.join(app.config["UPLOAD_FOLDER"], data_filename)

    # Save uploaded files with their original names
    data_file.save(data_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
