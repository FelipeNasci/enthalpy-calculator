from flask import Flask, request, render_template_string, send_file
from calculator import calculateEnthalpy, calculateMassFlow
from handleSpreadsheet import handleSpreadsheet
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

    if request.method == "POST":
        temperature = request.form.get("temperature", "10")
        pressure = request.form.get("pressure", "0")
        enthalpy_result = calculateEnthalpy(float(temperature), float(pressure))


    return render_template_string("""
<h1>Enthalpy Calculator</h1>

<form method="POST">
  <label>Temperature:</label><br>
  <input type="text" name="temperature" required value="{{ temperature }}"><br>

  <label>Pressure:</label><br>
  <input type="text" name="pressure" required value="{{ pressure }}"><br><br>

  <input type="submit" value="Calculate">
</form>

{% if enthalpy_result is not none %}
<h2>Result:</h2>
<p><strong>Enthalpy: {{ enthalpy_result }} kJ/kg</strong></p>
{% endif %}
""", temperature=temperature, pressure=pressure, enthalpy_result=enthalpy_result)

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
<h1>Enthalpy Calculator - XLSX Upload</h1>

<p>Upload an XLSX file to calculate and add enthalpy values.</p>

<form method="POST" enctype="multipart/form-data">
  <label>Temperature Column Name:</label><br>
  <input type="text" name="temp_column" placeholder="e.g., Temperature" required><br><br>

  <label>Pressure Column Name:</label><br>
  <input type="text" name="pressure_column" placeholder="e.g., Pressure" required><br><br>

  <label>Enthalpy Output Column Name:</label><br>
  <input type="text" name="enthalpy_column" placeholder="e.g., Enthalpy" required><br><br>

  <label>Upload XLSX File:</label><br>
  <input type="file" name="file" accept=".xlsx" required><br><br>

  <input type="submit" value="Process File">
</form>

{% if success_message %}
<p style="color: green;"><strong>✓ {{ success_message }}</strong></p>
<p>Temperature Column: <strong>{{ temp_column }}</strong></p>
<p>Pressure Column: <strong>{{ pressure_column }}</strong></p>
<p>Enthalpy Output Column: <strong>{{ enthalpy_column }}</strong></p>
{% if download_link %}
<p><a href="{{ download_link }}" style="color: blue; text-decoration: underline;">Download newFile.xlsx</a></p>
{% endif %}
{% endif %}

{% if error_message %}
<p style="color: red;"><strong>✗ Error: {{ error_message }}</strong></p>
{% endif %}
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
<h1>Mass Flow</h1>

<form method="POST">
  <label>Temperature Input (°C):</label><br>
  <input type="text" name="temperature_input" placeholder="Enter temperature" required><br><br>

  <label>Temperature Output (°C):</label><br>
  <input type="text" name="temperature_output" placeholder="Temperature output" required><br><br>

  <label>Pressure Input (kg/cm²):</label><br>
  <input type="text" name="pressure_input" placeholder="Enter pressure" required><br><br>

  <label>Pressure Output (kg/cm²):</label><br>
  <input type="text" name="pressure_output" placeholder="Pressure output" required><br><br>

  <label>Boiler Efficiency (%):</label><br>
  <input type="text" name="boilerEfficiency" placeholder="Enter boiler efficiency" required><br><br>

  <label>Machine Efficiency (%):</label><br>
  <input type="text" name="machineEfficiency" placeholder="Enter machine efficiency" required><br><br>

  <label>Electrical Work:</label><br>
  <input type="text" name="ElectricalWork" placeholder="Enter electrical work" required><br><br>

  <input type="submit" value="Calculate Flow">
</form>

{% if result is not none %}
<h2 style="color: green;">✓ Calculation Result:</h2>
<p><strong>Mass Flow: {{ result }} kg/s</strong></p>
{% endif %}

{% if error_message %}
<p style="color: red;"><strong>✗ Error: {{ error_message }}</strong></p>
{% endif %}
""", result=result, error_message=error_message)

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