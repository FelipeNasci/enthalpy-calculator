from flask import Flask, request, render_template_string, send_file
from calculator import calculateEnthalpy, calculateMassFlow
from handleSpreadsheet import handleSpreadsheet, receiveCalcSheetParams
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route("/", methods=["GET", "POST"])
def hello_world():
    temperature = request.args.get("temperature")
    pressure = request.args.get("pressure")
    enthalpy_result = None
    error_message = None

    if request.method == "POST":
        try:
            temperature = request.form.get("temperature", "10")
            pressure = request.form.get("pressure", "0")
            temp_float = float(temperature)
            pressure_float = float(pressure)

            if temp_float <= 0:
                error_message = "Temperature must be greater than 0"
            elif pressure_float < 0:
                error_message = "Pressure cannot be negative"
            else:
                enthalpy_result = calculateEnthalpy(temp_float, pressure_float)
                if enthalpy_result is None:
                    error_message = "Unable to calculate enthalpy for the given parameters"
        except ValueError:
            error_message = "Please enter valid numeric values"
        except Exception as e:
            error_message = f"Error calculating enthalpy: {str(e)}"

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enthalpy Calculator</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 500px;
        }

        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: box-shadow 0.3s ease;
        }

        .card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .card-header h1 {
            font-size: 28px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .card-header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .card-content {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group:last-of-type {
            margin-bottom: 0;
        }

        label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #333;
            margin-bottom: 8px;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        .result-card {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 8px;
            padding: 24px;
            margin-top: 24px;
            text-align: center;
        }

        .result-card h2 {
            color: #2e7d32;
            font-size: 18px;
            margin-bottom: 12px;
            font-weight: 500;
        }

        .result-value {
            font-size: 32px;
            color: #1b5e20;
            font-weight: 700;
            line-height: 1.2;
        }

        .result-unit {
            font-size: 14px;
            color: #2e7d32;
            margin-top: 4px;
        }

        .error-card {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            color: white;
        }

        .error-card p {
            font-size: 14px;
            margin: 0;
        }

        .nav-links {
            text-align: center;
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid #eee;
        }

        .nav-links a {
            display: inline-block;
            margin: 0 12px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1>Enthalpy Calculator</h1>
                <p>Calculate thermodynamic enthalpy properties</p>
            </div>

            <div class="card-content">
                <form method="POST">
                    <div class="form-group">
                        <label for="temp">Temperature (°C)</label>
                        <input type="text" id="temp" name="temperature" placeholder="e.g., 100" value="{{ temperature or '' }}" required>
                    </div>

                    <div class="form-group">
                        <label for="press">Pressure (kg/cm²)</label>
                        <input type="text" id="press" name="pressure" placeholder="e.g., 10" value="{{ pressure or '' }}" required>
                    </div>

                    <button type="submit">Calculate Enthalpy</button>
                </form>

                {% if enthalpy_result is not none %}
                <div class="result-card">
                    <h2>✓ Calculation Result</h2>
                    <div class="result-value">{{ enthalpy_result }}</div>
                    <div class="result-unit">kJ/kg</div>
                </div>
                {% endif %}

                {% if error_message %}
                <div class="error-card">
                    <p>✗ {{ error_message }}</p>
                </div>
                {% endif %}

                <div class="nav-links">
                    <a href="/upload">Upload File</a>
                    <a href="/flow">Mass Flow</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""", temperature=temperature, pressure=pressure, enthalpy_result=enthalpy_result, error_message=error_message)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    success_message = None
    error_message = None
    uploaded_file = None
    temp_column = None
    pressure_column = None
    enthalpy_column = None
    download_link = None

    if request.method == "POST":
        temp_column = request.form.get("temp_column", "").strip()
        pressure_column = request.form.get("pressure_column", "").strip()
        enthalpy_column = request.form.get("enthalpy_column", "").strip()

        if not temp_column or not pressure_column or not enthalpy_column:
            error_message = "Please specify Temperature, Pressure, and Enthalpy column names"
        elif 'file' not in request.files:
            error_message = "No file uploaded"
            print('file is not in files')
        else:
            file = request.files['file']
            if file.filename == '':
                error_message = "No file selected"
            elif not file.filename.endswith('.xlsx'):
                error_message = "Only .xlsx files are accepted"
            else:
                try:
                    print("\n" + "="*50)
                    print("XLSX File Upload and Processing")
                    print("="*50)

                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    print(f"File saved to: {filepath}")
                    print(f"Temperature column: {temp_column}")
                    print(f"Pressure column: {pressure_column}")
                    print(f"Enthalpy output column: {enthalpy_column}")

                    # Call handleSpreadsheet to process the file
                    print("\nCalling handleSpreadsheet...")
                    handleSpreadsheet(filepath, temp_column, pressure_column, enthalpy_column)

                    uploaded_file = filename
                    success_message = f"File '{filename}' successfully processed"
                    download_link = "/download"
                    print(success_message)
                    print("Output file created: newFile.xlsx")
                    print("="*50 + "\n")

                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    print(f"Error occurred: {error_message}")

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Enthalpy File</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 550px;
        }

        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: box-shadow 0.3s ease;
        }

        .card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .card-header h1 {
            font-size: 28px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .card-header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .card-content {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group:last-of-type {
            margin-bottom: 0;
        }

        label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #333;
            margin-bottom: 8px;
        }

        input[type="text"],
        input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        input[type="text"]:focus,
        input[type="file"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        .success-card {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 8px;
            padding: 24px;
            margin-top: 24px;
        }

        .success-card h2 {
            color: #2e7d32;
            font-size: 18px;
            margin-bottom: 12px;
            font-weight: 500;
        }

        .success-info {
            color: #1b5e20;
            font-size: 14px;
            margin-bottom: 8px;
            line-height: 1.6;
        }

        .success-info strong {
            font-weight: 600;
        }

        .download-link {
            display: inline-block;
            margin-top: 12px;
            padding: 10px 20px;
            background: white;
            color: #2e7d32;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .download-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3);
        }

        .error-card {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            color: white;
        }

        .error-card p {
            font-size: 14px;
            margin: 0;
        }

        .nav-links {
            text-align: center;
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid #eee;
        }

        .nav-links a {
            display: inline-block;
            margin: 0 12px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: #764ba2;
        }

        .form-hint {
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1>Upload XLSX File</h1>
                <p>Add enthalpy calculations to your spreadsheet</p>
            </div>

            <div class="card-content">
                <form method="POST" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="temp_col">Temperature Column Name</label>
                        <input type="text" id="temp_col" name="temp_column" placeholder="e.g., Temperature" required>
                        <div class="form-hint">Name of the column containing temperature values</div>
                    </div>

                    <div class="form-group">
                        <label for="press_col">Pressure Column Name</label>
                        <input type="text" id="press_col" name="pressure_column" placeholder="e.g., Pressure" required>
                        <div class="form-hint">Name of the column containing pressure values</div>
                    </div>

                    <div class="form-group">
                        <label for="enth_col">Enthalpy Output Column Name</label>
                        <input type="text" id="enth_col" name="enthalpy_column" placeholder="e.g., Enthalpy" required>
                        <div class="form-hint">Name of the new column for calculated enthalpy values</div>
                    </div>

                    <div class="form-group">
                        <label for="file_upload">Select XLSX File</label>
                        <input type="file" id="file_upload" name="file" accept=".xlsx" required>
                        <div class="form-hint">Maximum file size: 16 MB</div>
                    </div>

                    <button type="submit">Process File</button>
                </form>

                {% if success_message %}
                <div class="success-card">
                    <h2>✓ File Processed Successfully</h2>
                    <div class="success-info">
                        <strong>File:</strong> {{ uploaded_file }}<br>
                        <strong>Temperature Column:</strong> {{ temp_column }}<br>
                        <strong>Pressure Column:</strong> {{ pressure_column }}<br>
                        <strong>Enthalpy Column:</strong> {{ enthalpy_column }}
                    </div>
                    {% if download_link %}
                    <a href="{{ download_link }}" class="download-link">Download processed_enthalpy.xlsx</a>
                    {% endif %}
                </div>
                {% endif %}

                {% if error_message %}
                <div class="error-card">
                    <p>✗ {{ error_message }}</p>
                </div>
                {% endif %}

                <div class="nav-links">
                    <a href="/">Enthalpy Calculator</a>
                    <a href="/flow">Mass Flow</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""", success_message=success_message, error_message=error_message, uploaded_file=uploaded_file,
     temp_column=temp_column, pressure_column=pressure_column, enthalpy_column=enthalpy_column,
     download_link=download_link)

@app.route("/flow", methods=["GET", "POST"])
def flow():
    result = None
    error_message = None

    if request.method == "POST":
        try:
            temperature_input = float(request.form.get("temperature_input", 0))
            temperature_output = float(request.form.get("temperature_output", 0))
            pressure_input = float(request.form.get("pressure_input", 0))
            pressure_output = float(request.form.get("pressure_output", 0))
            boiler_efficiency = float(request.form.get("boilerEfficiency", 0)) / 100
            machine_efficiency = float(request.form.get("machineEfficiency", 0)) / 100
            electrical_work = float(request.form.get("ElectricalWork", 0))

            if temperature_input <= 0 or pressure_input <= 0:
                error_message = "Temperature Input and Pressure Input must be greater than 0"
            elif boiler_efficiency <= 0 or machine_efficiency <= 0:
                error_message = "Boiler Efficiency and Machine Efficiency must be greater than 0"
            elif electrical_work <= 0:
                error_message = "Electrical Work must be greater than 0"
            else:
                result = calculateMassFlow(
                    temperature_input,
                    temperature_output,
                    pressure_input,
                    pressure_output,
                    electrical_work,
                    boiler_efficiency,
                    machine_efficiency
                )
                result = round(result, 3)
                print(f"\nMass Flow Calculation:")
                print(f"  Temperature Input: {temperature_input}°C")
                print(f"  Temperature Output: {temperature_output}°C")
                print(f"  Pressure Input: {pressure_input} kg/cm²")
                print(f"  Pressure Output: {pressure_output} kg/cm²")
                print(f"  Boiler Efficiency: {boiler_efficiency*100}%")
                print(f"  Machine Efficiency: {machine_efficiency*100}%")
                print(f"  Electrical Work: {electrical_work}")
                print(f"  Mass Flow Result: {result} kg/s\n")

        except ValueError as e:
            error_message = f"Invalid input: Please enter valid numeric values"
        except Exception as e:
            error_message = f"Error calculating mass flow: {str(e)}"

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mass Flow Calculator</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 600px;
        }

        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: box-shadow 0.3s ease;
        }

        .card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .card-header h1 {
            font-size: 28px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .card-header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .card-content {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group:last-of-type {
            margin-bottom: 0;
        }

        label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #333;
            margin-bottom: 8px;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        .result-card {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 8px;
            padding: 24px;
            margin-top: 24px;
            text-align: center;
        }

        .result-card h2 {
            color: #2e7d32;
            font-size: 18px;
            margin-bottom: 12px;
            font-weight: 500;
        }

        .result-value {
            font-size: 32px;
            color: #1b5e20;
            font-weight: 700;
            line-height: 1.2;
        }

        .result-unit {
            font-size: 14px;
            color: #2e7d32;
            margin-top: 4px;
        }

        .error-card {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            color: white;
        }

        .error-card p {
            font-size: 14px;
            margin: 0;
        }

        .material-icons {
            font-size: 20px;
            vertical-align: middle;
            margin-right: 8px;
        }

        .nav-links {
            text-align: center;
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid #eee;
        }

        .nav-links a {
            display: inline-block;
            margin: 0 12px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1>Mass Flow Calculator</h1>
                <p>Calculate thermodynamic mass flow parameters</p>
            </div>

            <div class="card-content">
                <form method="POST">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="temp_in">Temperature Input (°C)</label>
                            <input type="text" id="temp_in" name="temperature_input" placeholder="e.g., 100" required>
                        </div>
                        <div class="form-group">
                            <label for="temp_out">Temperature Output (°C)</label>
                            <input type="text" id="temp_out" name="temperature_output" placeholder="e.g., 50" required>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="press_in">Pressure Input (kg/cm²)</label>
                            <input type="text" id="press_in" name="pressure_input" placeholder="e.g., 10" required>
                        </div>
                        <div class="form-group">
                            <label for="press_out">Pressure Output (kg/cm²)</label>
                            <input type="text" id="press_out" name="pressure_output" placeholder="e.g., 1" required>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="boiler">Boiler Efficiency (%)</label>
                            <input type="text" id="boiler" name="boilerEfficiency" placeholder="e.g., 85" required>
                        </div>
                        <div class="form-group">
                            <label for="machine">Machine Efficiency (%)</label>
                            <input type="text" id="machine" name="machineEfficiency" placeholder="e.g., 90" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="work">Electrical Work</label>
                        <input type="text" id="work" name="ElectricalWork" placeholder="e.g., 1000" required>
                    </div>

                    <button type="submit">Calculate Flow</button>
                </form>

                {% if result is not none %}
                <div class="result-card">
                    <h2>✓ Calculation Result</h2>
                    <div class="result-value">{{ result }}</div>
                    <div class="result-unit">kg/s</div>
                </div>
                {% endif %}

                {% if error_message %}
                <div class="error-card">
                    <p>✗ {{ error_message }}</p>
                </div>
                {% endif %}

                <div class="nav-links">
                    <a href="/">Enthalpy Calculator</a>
                    <a href="/upload">Upload File</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""", result=result, error_message=error_message)


@app.route("/calc-sheet", methods=["GET", "POST"])
def calc_sheet():
    if request.method == "POST":
        filepath = None
        if request.files.get("file") and request.files["file"].filename:
            filename = secure_filename(request.files["file"].filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            request.files["file"].save(filepath)
        receiveCalcSheetParams(
            filepath,
            request.form.get("temp_input_column"),
            request.form.get("temp_output_column"),
            request.form.get("pressure_input_column"),
            request.form.get("pressure_output_column"),
            request.form.get("boiler_efficiency"),
            request.form.get("machine_efficiency"),
            request.form.get("electrical_work"),
        )

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculate Spreadsheet</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 600px;
        }

        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: box-shadow 0.3s ease;
        }

        .card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .card-header h1 {
            font-size: 28px;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .card-header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .card-content {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group:last-of-type {
            margin-bottom: 0;
        }

        label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #333;
            margin-bottom: 8px;
        }

        input[type="text"],
        input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        input[type="text"]:focus,
        input[type="file"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        button {
            width: 100%;
            padding: 12px;
            margin-top: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        .material-icons {
            font-size: 20px;
            vertical-align: middle;
            margin-right: 8px;
        }

        .nav-links {
            text-align: center;
            margin-top: 24px;
            padding-top: 24px;
            border-top: 1px solid #eee;
        }

        .nav-links a {
            display: inline-block;
            margin: 0 12px;
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: #764ba2;
        }

        .validation-error {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 16px;
            color: white;
            font-size: 14px;
            display: none;
        }

        .validation-error.visible {
            display: block;
        }

        input:invalid:not(:placeholder-shown) {
            border-color: #ff6b6b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1>Calculate Spreadsheet</h1>
                <p>Upload XLSX and indicate column names (frontend only)</p>
            </div>

            <div class="card-content">
                <form method="POST" enctype="multipart/form-data" id="calc-sheet-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="temp_in_col">Temperature Input Column Name</label>
                            <input type="text" id="temp_in_col" name="temp_input_column" placeholder="e.g., Temp In" required minlength="1">
                        </div>
                        <div class="form-group">
                            <label for="temp_out_col">Temperature Output Column Name</label>
                            <input type="text" id="temp_out_col" name="temp_output_column" placeholder="e.g., Temp Out" required minlength="1">
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="press_in_col">Pressure Input Column Name</label>
                            <input type="text" id="press_in_col" name="pressure_input_column" placeholder="e.g., Pressure In" required minlength="1">
                        </div>
                        <div class="form-group">
                            <label for="press_out_col">Pressure Output Column Name</label>
                            <input type="text" id="press_out_col" name="pressure_output_column" placeholder="e.g., Pressure Out" required minlength="1">
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="boiler_val">Boiler Efficiency (%)</label>
                            <input type="text" id="boiler_val" name="boiler_efficiency" placeholder="e.g., 85" required minlength="1">
                        </div>
                        <div class="form-group">
                            <label for="machine_val">Machine Efficiency (%)</label>
                            <input type="text" id="machine_val" name="machine_efficiency" placeholder="e.g., 90" required minlength="1">
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="electrical_val">Electrical Work (constant)</label>
                        <input type="text" id="electrical_val" name="electrical_work" placeholder="e.g., 1000" required minlength="1">
                    </div>

                    <div class="form-group">
                        <label for="file_upload">Select XLSX File</label>
                        <input type="file" id="file_upload" name="file" accept=".xlsx" required>
                        <div class="form-hint" style="font-size:12px;color:#999;margin-top:4px;">Only .xlsx files. Max 16 MB.</div>
                    </div>

                    <div class="validation-error" id="validation-message" role="alert"></div>

                    <button type="submit">Upload (UI only)</button>
                </form>

                <script>
                    document.getElementById('calc-sheet-form').addEventListener('submit', function(e) {
                        var msgEl = document.getElementById('validation-message');
                        msgEl.classList.remove('visible');
                        msgEl.textContent = '';

                        var fileInput = document.getElementById('file_upload');
                        if (fileInput.files.length === 0) {
                            e.preventDefault();
                            msgEl.textContent = 'Please select an XLSX file.';
                            msgEl.classList.add('visible');
                            return;
                        }
                        var file = fileInput.files[0];
                        var name = file.name.toLowerCase();
                        if (!name.endsWith('.xlsx')) {
                            e.preventDefault();
                            msgEl.textContent = 'Only .xlsx files are accepted.';
                            msgEl.classList.add('visible');
                            return;
                        }
                        if (file.size > 16 * 1024 * 1024) {
                            e.preventDefault();
                            msgEl.textContent = 'File size must be 16 MB or less.';
                            msgEl.classList.add('visible');
                            return;
                        }

                        var textInputs = this.querySelectorAll('input[type="text"]');
                        for (var i = 0; i < textInputs.length; i++) {
                            if (!textInputs[i].value.trim()) {
                                e.preventDefault();
                                msgEl.textContent = 'Please fill in all fields.';
                                msgEl.classList.add('visible');
                                textInputs[i].focus();
                                return;
                            }
                        }
                    });
                </script>

                <div class="nav-links">
                    <a href="/">Enthalpy Calculator</a>
                    <a href="/upload">Upload</a>
                    <a href="/flow">Mass Flow</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""")


@app.route("/download")
def download():
    try:
        print("\n" + "="*50)
        print("Download Request: newFile.xlsx")
        print("="*50)

        # Check if file exists
        if not os.path.exists("newFile.xlsx"):
            print("Error: newFile.xlsx not found")
            return "File not found. Please process a file first.", 404

        print(f"File size: {os.path.getsize('newFile.xlsx')} bytes")
        print("Serving file to client...")

        # Send the file to client with proper MIME type
        return send_file(
            "newFile.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="processed_enthalpy.xlsx"
        )
    except Exception as e:
        print(f"Download error: {str(e)}")
        return f"Error downloading file: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
