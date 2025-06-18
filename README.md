# GeoNode-GeoServer Integration Test Suite

A comprehensive testing framework for validating GeoNode and GeoServer integration using Kestra workflows and Jupyter notebooks.

## Overview

This project provides automated testing capabilities for GeoNode-GeoServer deployments, ensuring proper integration, data publishing, and OGC service functionality. The test suite is designed with security, reliability, and maintainability in mind.

## Features

### 🔒 Security
- Environment variable-based credential management
- Secure CSRF token handling
- Input validation and sanitization
- No hardcoded credentials in code

### 🛡️ Reliability
- Robust error handling and retry mechanisms
- Comprehensive logging and monitoring
- Timeout management for long-running operations
- Graceful failure handling

### 📊 Comprehensive Testing
- GeoNode authentication and session management
- Data upload testing (vector and raster)
- GeoServer datastore and coverage store verification
- WMS and WFS service testing
- Layer publishing validation

### 🔧 Maintainability
- Modular code structure with type hints
- Comprehensive documentation and comments
- Configurable test parameters
- Clean separation of concerns

## Project Structure

```
test_geonode-geoserver/
├── data/                           # Test data files
│   ├── sample_vector.shp          # Sample shapefile for testing
│   ├── sample_vector.dbf          # Shapefile database
│   ├── sample_vector.prj          # Projection file
│   ├── sample_vector.shx          # Shapefile index
│   └── sample_raster.tif          # Sample raster for testing
├── kestra_flows/                   # Kestra workflow definitions
│   └── geonode_geoserver_test_flow.yml
├── notebooks/                      # Jupyter notebooks
│   ├── geonode_geoserver_tests.ipynb          # Original test notebook
│   └── geonode_geoserver_tests_improved.ipynb # Enhanced test notebook
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## Prerequisites

### Software Requirements
- Python 3.8+
- Jupyter Notebook
- Kestra (for workflow execution)
- GeoNode instance (running)
- GeoServer instance (running)

### Python Dependencies
Install required packages using:
```bash
pip install -r requirements.txt
```

Key dependencies include:
- `requests` - HTTP client library
- `papermill` - Notebook execution engine
- `geopandas` - Geospatial data processing
- `owslib` - OGC web service client
- `jupyter` - Notebook environment

## Configuration

### Environment Variables

For security, configure the following environment variables:

```bash
# Service URLs
export GEONODE_URL="http://your-geonode-instance:8000"
export GEOSERVER_URL="http://your-geoserver-instance:8080/geoserver"

# Authentication
export GEONODE_USERNAME="your-username"
export GEONODE_PASSWORD="your-password"

# Test Data Paths
export SAMPLE_SHAPEFILE_PATH="./data/sample_vector.shp"
export SAMPLE_RASTER_PATH="./data/sample_raster.tif"

# Optional Configuration
export DEFAULT_TIMEOUT="30"
export MAX_RETRY_ATTEMPTS="3"
export ENABLE_CLEANUP="false"
export VERBOSE_LOGGING="false"
```

### Kestra Configuration

The Kestra workflow accepts the following input parameters:
- `geonode_url` - GeoNode instance URL
- `geoserver_url` - GeoServer instance URL
- `username` - Authentication username
- `password` - Authentication password
- `sample_shapefile_path` - Path to test shapefile
- `sample_raster_path` - Path to test raster
- `test_environment` - Environment identifier
- `notification_webhook` - Optional webhook for notifications

## Usage

### Running Tests Locally

#### Option 1: Direct Jupyter Notebook Execution
```bash
# Start Jupyter
jupyter notebook

# Open and run notebooks/geonode_geoserver_tests_improved.ipynb
```

#### Option 2: Papermill Execution
```bash
# Execute notebook with Papermill
papermill \
    notebooks/geonode_geoserver_tests_improved.ipynb \
    notebooks/output_test_results.ipynb \
    --log-output \
    --progress-bar
```

### Running Tests with Kestra

1. **Deploy the workflow:**
   ```bash
   kestra flow deploy kestra_flows/geonode_geoserver_test_flow.yml
   ```

2. **Execute manually:**
   ```bash
   kestra flow execute dev_tests geonode_geoserver_tests
   ```

3. **Execute with custom parameters:**
   ```bash
   kestra flow execute dev_tests geonode_geoserver_tests \
     --inputs geonode_url=http://custom-geonode:8000 \
     --inputs username=testuser
   ```

### Automated Execution

The workflow includes predefined triggers:
- **Daily Health Check**: Runs at 6 AM daily (disabled by default)
- **Weekly Comprehensive Test**: Runs Monday at 2 AM (disabled by default)

Enable triggers by setting `disabled: false` in the workflow configuration.

## Test Cases

The test suite includes the following test cases:

### 1. Authentication and Session Management
- GeoNode login validation
- CSRF token handling
- Session persistence
- GeoServer authentication

### 2. Data Upload Testing
- Shapefile upload to GeoNode
- GeoTIFF upload to GeoNode
- File validation and error handling
- Upload progress monitoring

### 3. GeoServer Integration
- Datastore creation verification
- Coverage store creation verification
- Layer publishing validation
- Workspace management

### 4. OGC Service Testing
- WMS GetMap requests
- WFS GetFeature requests
- Service capability validation
- Response format verification

### 5. Error Handling and Recovery
- Network timeout handling
- Authentication failure recovery
- Invalid data handling
- Service unavailability scenarios

## Monitoring and Logging

### Log Levels
- `INFO`: General test progress and results
- `DEBUG`: Detailed execution information (when `VERBOSE_LOGGING=true`)
- `ERROR`: Test failures and exceptions
- `WARNING`: Non-critical issues and fallbacks

### Test Results
Test results are stored in the `test_results` dictionary with the following structure:
```json
{
  "test_name": {
    "status": "SUCCESS|FAILURE",
    "message": "Descriptive message",
    "duration": 1.23,
    "timestamp": "2024-01-01T12:00:00",
    "metadata": {}
  }
}
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify GeoNode/GeoServer URLs are correct
   - Check if services are running
   - Validate network connectivity

2. **Authentication Failures**
   - Verify username/password credentials
   - Check if account is active
   - Ensure proper environment variable configuration

3. **File Upload Errors**
   - Validate file paths and permissions
   - Check file size limits
   - Ensure proper file formats

4. **CSRF Token Issues**
   - Clear browser cookies if testing manually
   - Verify GeoNode CSRF configuration
   - Check for proper session handling

### Debug Mode
Enable verbose logging for detailed troubleshooting:
```bash
export VERBOSE_LOGGING="true"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper tests
4. Update documentation as needed
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and returns
- Include comprehensive docstrings
- Add appropriate error handling

## Security Considerations

- Never commit credentials to version control
- Use environment variables for sensitive configuration
- Regularly update dependencies for security patches
- Validate all user inputs
- Use HTTPS in production environments

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information
4. Include environment details and error messages
