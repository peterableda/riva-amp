# Riva Transcriptor Service - Deployment Guide

This guide provides step-by-step instructions for deploying the Riva Transcriptor Service AMP in Cloudera Machine Learning (CML).

## Prerequisites

### 1. NVIDIA Riva Endpoint
- You must have access to a running NVIDIA Riva ASR (Automatic Speech Recognition) service
- The service should expose REST API endpoints for transcription and translation
- Note the base URL of your Riva service (e.g., `https://your-riva-endpoint.com/v1`)

### 2. CML Environment
- Cloudera Machine Learning workspace with appropriate permissions
- Access to deploy AMPs or create new projects
- Network connectivity to the Riva service endpoint

### 3. JWT Token Access
- The service uses JWT tokens for authentication with the Riva backend
- In CML workbench environments, tokens are automatically available at `/tmp/jwt`

## Deployment Steps

### Option 1: Deploy from AMP Catalog (Recommended)

1. **Navigate to Prototype Catalog**
   - Open your CML workspace
   - Go to the "Prototype Catalog" section
   - Search for "Riva Transcriptor Service"

2. **Launch the AMP**
   - Click on the AMP tile
   - Click "Launch as Project"
   - Provide a project name (e.g., "Riva Transcriptor Service")

3. **Configure Environment Variables**
   - Set `RIVA_BASE_URL` to your Riva service endpoint
   - Example: `https://ml-xxxx.your-domain.com/namespaces/serving-default/endpoints/nemo-riva-asr-whisper/v1`
   - Click "Configure Project"

4. **Monitor Deployment**
   - The AMP will automatically run the following steps:
     - Environment validation
     - Dependency installation
     - Service setup and connectivity testing
     - Application deployment

### Option 2: Manual Deployment

1. **Create New Project**
   - In CML, click "New Project"
   - Choose "Git" as the initial setup
   - Clone this repository URL
   - Set the project name and description

2. **Set Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add `RIVA_BASE_URL` with your Riva endpoint URL

3. **Run Setup Steps**
   ```bash
   # Step 1: Validate environment
   python 0_session-validate/validate.py

   # Step 2: Install dependencies
   python 1_session-install-deps/install.py

   # Step 3: Setup and test service
   python 2_job-setup/setup.py
   ```

4. **Deploy Application**
   - Create a new application in CML
   - Set the script path to `3_app/app.py`
   - Configure resources: 2 CPU, 8GB Memory
   - Add environment variable `RIVA_BASE_URL`
   - Deploy the application

## Configuration Details

### Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `RIVA_BASE_URL` | Base URL for Riva service | `https://your-riva.com/v1` | Yes |
| `CDSW_APP_PORT` | Application port | `7860` | No (auto-set) |

### Resource Requirements

| Component | CPU | Memory | Storage | GPU |
|-----------|-----|---------|---------|-----|
| Validation Session | 1 | 2GB | 1GB | No |
| Install Session | 2 | 4GB | 2GB | No |
| Setup Job | 2 | 4GB | 2GB | No |
| Application | 2 | 8GB | 10GB | No |

## Post-Deployment Verification

### 1. Check Application Status
- Navigate to the Applications section in CML
- Verify the "Riva Transcriptor Service" is running
- Note the application URL

### 2. Test Basic Functionality
- Access the application URL
- Try the microphone recording feature (requires HTTPS and browser permissions)
- Upload a test audio file
- Verify transcription results

### 3. Test API Connectivity
- Check the application logs for any connection errors
- Verify JWT token authentication is working
- Test with different audio formats and languages

## Common Deployment Issues

### 1. Environment Variable Not Set
**Error**: `RIVA_BASE_URL environment variable is not set`
**Solution**: Set the environment variable in AMP configuration or project settings

### 2. Riva Service Connection Failed
**Error**: `Could not connect to Riva service`
**Solutions**:
- Verify Riva service is running and accessible
- Check network connectivity from CML to Riva endpoint
- Validate the URL format includes `/v1` suffix
- Ensure JWT token is available and valid

### 3. Dependency Installation Failed
**Error**: Various package installation errors
**Solutions**:
- Check internet connectivity for package downloads
- Verify pip is working correctly
- Check for system-level dependency conflicts
- Run installation steps individually to isolate issues

### 4. Audio Processing Errors
**Error**: `ffmpeg` or audio library errors
**Solutions**:
- Ensure `cdsw-build.sh` was executed successfully
- Check if system audio libraries are installed
- Verify audio file formats are supported

### 5. Microphone Not Working
**Error**: Browser microphone access denied
**Solutions**:
- Ensure the application is accessed via HTTPS
- Allow microphone permissions in browser
- Try a different browser (Chrome/Firefox recommended)
- Check if corporate firewall blocks media access

## Testing the Deployment

### 1. Microphone Test
```
1. Access the application
2. Go to "Microphone Recording" tab
3. Click record and speak clearly
4. Stop recording and click "Transcribe"
5. Verify accurate transcription appears
```

### 2. File Upload Test
```
1. Prepare a test audio file (WAV recommended)
2. Go to "File Upload" tab
3. Upload the file
4. Select appropriate language
5. Click "Transcribe File"
6. Verify results and status messages
```

### 3. Multi-language Test
```
1. Test with audio in different languages
2. Verify language selection affects results
3. Test translation functionality
4. Check status messages for format conversion info
```

## Monitoring and Maintenance

### 1. Application Logs
- Monitor application logs for errors or warnings
- Check for API connectivity issues
- Watch for audio processing errors

### 2. Performance Monitoring
- Track response times for transcription requests
- Monitor resource usage (CPU, memory)
- Check for file cleanup and temporary storage usage

### 3. Security Considerations
- Regularly review JWT token access
- Monitor network traffic to Riva endpoint
- Ensure temporary audio files are properly cleaned up
- Review access logs for unusual activity

## Scaling and Performance

### 1. Resource Scaling
- Increase CPU/memory if processing large files
- Consider multiple application instances for load balancing
- Monitor storage usage for temporary file processing

### 2. Optimization Tips
- Use WAV format files for best performance
- Keep audio file sizes under 100MB
- Specify correct language for better accuracy
- Use clear, noise-free audio recordings

## Support and Troubleshooting

### 1. Logs to Check
- CML application logs
- Session execution logs
- Job execution logs
- System logs (if accessible)

### 2. Key Information to Collect
- Riva service endpoint and status
- JWT token availability and validity
- Audio file formats and sizes being processed
- Browser and client environment details
- Network connectivity between CML and Riva

### 3. Getting Help
- Review this deployment guide
- Check the main README.md for detailed documentation
- Consult CML documentation for platform-specific issues
- Contact your Cloudera administrator for infrastructure problems

---

**Success Criteria**:
- ✅ Application deploys without errors
- ✅ Microphone recording works in browser
- ✅ File upload and transcription succeeds
- ✅ Multiple languages are supported
- ✅ Audio format conversion works automatically
- ✅ Status messages provide clear feedback
