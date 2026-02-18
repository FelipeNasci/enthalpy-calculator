# Enthalpy Calculator

A Flask web application for calculating water enthalpy values based on temperature and pressure using the CoolProp library.

## Features

- **Calculator Route (`/`)**: Calculate single enthalpy values by entering temperature and pressure
- **Upload Route (`/upload`)**: Process XLSX files with temperature and pressure columns
- **Automatic Enthalpy Calculation**: Uses handleSpreadsheet to calculate enthalpy for entire datasets
- **File Download**: Download processed files with calculated enthalpy values

## Project Structure

```
calculator-enthalpy/
├── hello.py                 # Flask application
├── calculator.py            # Enthalpy calculation logic
├── handleSpreadsheet.py     # Spreadsheet processing
├── wsgi.py                  # WSGI entry point for production
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Docker Compose for local/production deployment
├── .env.example            # Environment variables template
└── uploads/                # Directory for uploaded files (auto-created)
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, for containerized deployment)
- pip (Python package manager)

## Local Development Setup

### 1. Clone and Navigate

```bash
cd calculator-enthalpy
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your configuration if needed
```

### 5. Run Application

**Development Mode:**
```bash
python hello.py
```

**Production Mode (with gunicorn):**
```bash
gunicorn --bind 0.0.0.0:5010 --workers 4 wsgi:app
```

Application will be available at `http://localhost:5010`

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Using Docker Directly

```bash
# Build image
docker build -t enthalpy-calculator .

# Run container
docker run -p 5010:5010 -v $(pwd)/uploads:/app/uploads enthalpy-calculator
```

## API Endpoints

### `GET / or POST /`
Main calculator page for single enthalpy calculations.

**Parameters:**
- `temperature`: Temperature value (°C)
- `pressure`: Pressure value (kg/cm²)
- `enthalpy_result`: Calculated enthalpy (kJ/kg)

### `POST /upload`
Upload and process XLSX files with batch enthalpy calculations.

**Form Fields:**
- `temp_column`: Name of temperature column in Excel file
- `pressure_column`: Name of pressure column in Excel file
- `enthalpy_column`: Name for output enthalpy column
- `file`: XLSX file to process

**Response:**
- Success message with download link
- Processed file saved as `newFile.xlsx`

### `GET /download`
Download the processed Excel file with calculated enthalpy values.

**Response:**
- Excel file with original data + calculated enthalpy column
- Downloaded as `processed_enthalpy.xlsx`

## Usage Examples

### Using the Web Interface

1. Navigate to `http://localhost:5010/`
2. Enter temperature and pressure values
3. Click "Calculate"
4. View calculated enthalpy result

### Processing Batch Files

1. Navigate to `http://localhost:5010/upload`
2. Enter column names:
   - Temperature Column: `TEMPERATURA (°C)`
   - Pressure Column: `PRESSÃO (kg/cm²)`
   - Enthalpy Output: `Enthalpia (kJ/kg)`
3. Upload your XLSX file
4. Click "Process File"
5. Click download link to get processed file

## Configuration

Edit `.env` file for:
- `FLASK_ENV`: Set to `production` or `development`
- `PORT`: Application port (default: 5010)
- `UPLOAD_FOLDER`: Directory for file uploads
- `MAX_FILE_SIZE`: Maximum upload size in bytes

## Troubleshooting

**File not found error on download:**
- Ensure file upload and processing completed successfully
- Check console for error messages
- Verify `uploads/` directory exists

**CoolProp errors:**
- Ensure temperature > 0°C (returns 0 if ≤ 0)
- Check that pressure and temperature values are valid
- Review error messages in console

**Docker container won't start:**
- Check logs: `docker-compose logs`
- Ensure port 5010 is available
- Verify Docker daemon is running

## Production Deployment

### Using Docker

The Dockerfile is configured for production use with:
- Gunicorn as WSGI server
- 4 worker processes
- Health checks enabled
- Non-root user execution (recommended to add)

### Environment Configuration

Before deployment, ensure:

```bash
cp .env.example .env
# Edit .env with production values
```

### Scaling

Adjust Docker Compose for production:

```yaml
environment:
  - WORKERS=8  # Increase worker count
  - TIMEOUT=180  # Increase timeout for large files
```

## Performance Notes

- Large files (>10MB) may take longer to process
- Default timeout is 120 seconds
- Use multiple workers in production for concurrent requests
- Monitor disk space for file uploads/outputs

## Dependencies

- **Flask**: Web framework
- **pandas**: Data manipulation and Excel I/O
- **openpyxl**: Excel file handling
- **CoolProp**: Thermodynamic property calculations
- **gunicorn**: Production WSGI server
- **python-dotenv**: Environment variable management

## License

This project uses CoolProp library - see their documentation for licensing information.

## Support

For issues or questions:
1. Check console output for error messages
2. Review application logs in Docker: `docker-compose logs`
3. Verify input data format and column names
4. Ensure all dependencies are properly installed
