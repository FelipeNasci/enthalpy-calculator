# Deployment Guide

This guide provides step-by-step instructions for deploying the Enthalpy Calculator application.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Local Deployment](#docker-local-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Monitoring & Maintenance](#monitoring--maintenance)

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup Steps

1. **Clone repository**
   ```bash
   cd calculator-enthalpy
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Unix/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```

5. **Run application**
   ```bash
   make dev
   # or manually:
   FLASK_ENV=development python hello.py
   ```

6. **Access application**
   ```
   http://localhost:5010
   ```

## Docker Local Deployment

### Quick Start

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Commands

```bash
# Build image
docker build -t enthalpy-calculator .

# Run container
docker run -d \
  -p 5010:5010 \
  -v $(pwd)/uploads:/app/uploads \
  --name enthalpy-calc \
  enthalpy-calculator

# View logs
docker logs -f enthalpy-calc

# Stop container
docker stop enthalpy-calc
docker rm enthalpy-calc
```

## Production Deployment

### Using Docker Compose

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   sed -i 's/FLASK_ENV=.*/FLASK_ENV=production/' .env
   ```

2. **Create data volumes** (optional)
   ```bash
   docker volume create enthalpy-uploads
   ```

3. **Start services**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

4. **Verify deployment**
   ```bash
   curl http://localhost:5010
   docker-compose logs
   ```

### Using Gunicorn Directly

1. **Install production dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with gunicorn**
   ```bash
   make prod
   # or manually:
   gunicorn --bind 0.0.0.0:5010 \
     --workers 4 \
     --timeout 120 \
     --access-logfile - \
     --error-logfile - \
     wsgi:app
   ```

3. **Using systemd (Linux)**

   Create `/etc/systemd/system/enthalpy.service`:
   ```ini
   [Unit]
   Description=Enthalpy Calculator
   After=network.target

   [Service]
   Type=notify
   User=www-data
   WorkingDirectory=/app/calculator-enthalpy
   Environment="PATH=/app/calculator-enthalpy/venv/bin"
   ExecStart=/app/calculator-enthalpy/venv/bin/gunicorn \
     --workers 4 \
     --bind 127.0.0.1:5010 \
     wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```

   Then:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable enthalpy
   sudo systemctl start enthalpy
   sudo systemctl status enthalpy
   ```

### Using Reverse Proxy (Nginx)

1. **Install Nginx**
   ```bash
   sudo apt-get install nginx
   ```

2. **Configure `/etc/nginx/sites-available/enthalpy`**
   ```nginx
   upstream enthalpy_app {
       server 127.0.0.1:5010;
   }

   server {
       listen 80;
       server_name example.com;

       client_max_body_size 16M;

       location / {
           proxy_pass http://enthalpy_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static {
           alias /app/calculator-enthalpy/static;
       }
   }
   ```

3. **Enable site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/enthalpy /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Cloud Platforms

### Heroku

1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   heroku login
   ```

2. **Create Procfile**
   ```
   web: gunicorn --workers 4 --bind 0.0.0.0:$PORT wsgi:app
   ```

3. **Deploy**
   ```bash
   heroku create enthalpy-calculator
   git push heroku main
   ```

### AWS Lambda / Elastic Beanstalk

1. **Create `.ebextensions/python.config`**
   ```yaml
   option_settings:
     aws:elasticbeanstalk:application:environment:
       PYTHONPATH: /var/app/current:$PYTHONPATH
     aws:elasticbeanstalk:container:python:
       WSGIPath: wsgi:app
   ```

2. **Deploy**
   ```bash
   eb create enthalpy-calculator
   eb deploy
   ```

### Google Cloud Run

1. **Create `.gcloudignore`**
   ```
   __pycache__
   .git
   .env
   venv/
   ```

2. **Deploy**
   ```bash
   gcloud run deploy enthalpy-calculator \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Azure Container Instances

1. **Push image to registry**
   ```bash
   docker build -t enthalpy-calculator .
   docker tag enthalpy-calculator myregistry.azurecr.io/enthalpy-calculator
   docker push myregistry.azurecr.io/enthalpy-calculator
   ```

2. **Deploy container**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name enthalpy-calculator \
     --image myregistry.azurecr.io/enthalpy-calculator \
     --cpu 1 --memory 1 \
     --ports 5010 \
     --registry-login-server myregistry.azurecr.io \
     --registry-username <username> \
     --registry-password <password>
   ```

## Monitoring & Maintenance

### Health Checks

```bash
# Manual health check
curl http://localhost:5010/

# Check in docker-compose
docker-compose ps  # Shows health status
```

### Logs

```bash
# View logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service logs
docker-compose logs enthalpy-calculator

# Last 100 lines
docker-compose logs --tail 100
```

### Database Cleanup

```bash
# Remove old uploads (older than 30 days)
find uploads/ -type f -mtime +30 -delete

# Remove processed files
rm -f newFile.xlsx
```

### Backup

```bash
# Backup uploads
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/

# Backup to external storage
aws s3 cp uploads-backup-*.tar.gz s3://my-bucket/backups/
```

### Performance Tuning

**For High Load:**

1. **Increase workers in docker-compose.yml**
   ```yaml
   environment:
     - WORKERS=8
   ```

2. **Add load balancer** (Nginx example shown above)

3. **Enable caching**
   ```bash
   # Add Redis caching (optional future enhancement)
   ```

4. **Monitor resources**
   ```bash
   docker stats enthalpy-calculator
   ```

### Troubleshooting

**Container won't start:**
```bash
docker-compose logs enthalpy-calculator
docker-compose up --build
```

**Port already in use:**
```bash
# Change port in docker-compose.yml or:
docker-compose down
lsof -i :5010  # Check what's using the port
```

**File upload fails:**
```bash
# Check permissions
ls -la uploads/
chmod 755 uploads/

# Check disk space
df -h
```

**Application crashes:**
```bash
# Check logs immediately
docker-compose logs -f

# Restart
docker-compose restart
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file, use `.env.example`
2. **File Uploads**: Validate all uploaded files
3. **Dependencies**: Keep packages updated
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```
4. **HTTPS**: Use reverse proxy with SSL certificates (Let's Encrypt)
5. **Access Control**: Restrict upload file types and sizes
6. **Monitoring**: Set up alerts for failures

## Useful Makefile Commands

```bash
make install      # Install dependencies
make dev          # Run in development
make prod         # Run in production
make build        # Build Docker image
make up           # Start Docker services
make down         # Stop Docker services
make logs         # View logs
make clean        # Clean temporary files
make lint         # Run code linter
```

## Support & Troubleshooting

For deployment issues:
1. Check application logs
2. Verify all dependencies are installed
3. Ensure port 5010 is available
4. Check file permissions in uploads/ directory
5. Verify environment variables in .env file
