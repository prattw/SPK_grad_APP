# SPK Grad App Backend

Backend server for handling CSV generation and email sending for the SPK rock sample analysis app.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Update email configuration in `server.py`:
   - Set `EMAIL_USERNAME` to your email address
   - Set `EMAIL_PASSWORD` to your app password (not regular password)

3. Run the server:
```bash
python server.py
```

## API Endpoints

### POST /api/send-results
Sends analysis results as CSV via email.

**Request Body:**
```json
{
  "email": "user@usace.army.mil",
  "imageData": "base64_encoded_image_data",
  "analysisResults": "{\"grainCount\": 25, \"analyzedImage\": \"...\"}"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully to user@usace.army.mil",
  "timestamp": "2024-01-20T10:30:00"
}
```

### GET /api/health
Health check endpoint.

## Email Configuration

The server needs to be configured with:
- SMTP server settings (currently set for Gmail)
- Valid email credentials with app password

For USACE networking, you may need to use internal SMTP servers instead of Gmail.


