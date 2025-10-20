#!/usr/bin/env python3
"""
Backend server for SPK grad app - handles CSV generation and email sending
"""

from flask import Flask, request, jsonify
import os
import csv
import base64
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io

app = Flask(__name__)

# Email configuration - UPDATE THESE VALUES
# NOTE: You need to find the correct SMTP server for CCA
# Common options: smtp.gmail.com, smtp.outlook.com, or CCA's specific server
SMTP_SERVER = "smtp.gmail.com"  # Default - UPDATE with correct CCA SMTP server
SMTP_PORT = 587
EMAIL_USERNAME = "pratt@cca.edu"  # CCA email address
EMAIL_PASSWORD = "thiigjismzexedub"  # App password (should be exactly 16 chars)

def generate_csv_results(analysis_data, image_filename, email_address):
    """Generate CSV file with analysis results"""
    
    # Create CSV content
    csv_data = []
    csv_output = io.StringIO()
    
    # Header row
    headers = [
        "Analysis_ID",
        "Timestamp", 
        "Email_Address",
        "Image_Filename",
        "Grain_Count",
        "Average_Grain_Size",
        "Size_Distribution_SD",
        "Total_Sample_Area",
        "Notes"
    ]
    
    # Extract analysis results
    try:
        if analysis_data and analysis_data != 'null':
            results = json.loads(analysis_data)
            grain_count = results.get('grainCount', 'N/A')
        else:
            grain_count = 'Processing Failed'
    except:
        grain_count = 'Invalid Data'
    
    # Sample data row - replace with actual analysis results
    row = [
        f"SPK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",  # Analysis ID
        datetime.now().isoformat(),  # Timestamp
        email_address,  # Email address passed as parameter
        image_filename,
        grain_count,
        "2.5",  # Average grain size (mm) - replace with actual
        "1.8",  # Size distribution standard deviation - replace with actual
        "45.2",  # Total sample area (cm²) - replace with actual
        "Rock sample segmentation analysis complete"  # Notes
    ]
    
    # Write CSV
    writer = csv.writer(csv_output)
    writer.writerow(headers)
    writer.writerow(row)
    
    return csv_output.getvalue()

def send_email_with_csv(recipient_email, csv_content, image_filename):
    """Send email with CSV attachment"""
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = recipient_email
        msg['Subject'] = f"SPK Rock Sample Analysis Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Email body
        body = f"""
Dear {recipient_email.split('@')[0]},

Your rock sample analysis has been completed successfully.

Analysis Details:
- Analysis ID: SPK_{datetime.now().strftime('%Y%m%d_%H%M%S')}
- Image: {image_filename}
- Timestamp: {datetime.now().isoformat()}

Please find the detailed results attached as a CSV file.

Best regards,
USACE Sacramento District - SPK Analysis System
Sent from: pratt@cca.edu
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach CSV file
        csv_filename = f"SPK_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(csv_content.encode('utf-8'))
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename= {csv_filename}')
        msg.attach(attachment)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, recipient_email, text)
        server.quit()
        
        return True, f"Email sent successfully to {recipient_email}"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

@app.route('/api/send-results', methods=['POST'])
def send_results():
    """Handle CSV generation and email sending"""
    
    try:
        data = request.json
        
        # Validate required fields
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email address required'}), 400
            
        # Validate email domain
        valid_domains = ['usace.army.mil', 'usgs.gov']
        if not any(email.endswith(f'@{domain}') for domain in valid_domains):
            return jsonify({'error': 'Invalid email domain'}), 400
        
        # Get analysis results
        analysis_results = data.get('analysisResults', '{}')
        image_data = data.get('imageData', '')
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"rock_sample_{timestamp}.jpg"
        
        # Generate CSV
        csv_content = generate_csv_results(analysis_results, image_filename, email)
        
        # Send email
        success, message = send_email_with_csv(email, csv_content, image_filename)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test endpoint to send a test email with CSV"""
    try:
        data = request.json or {}
        test_email_addr = data.get('email', 'william.a.pratt@usace.army.mil')
        
        # Validate email domain for test
        valid_domains = ['usace.army.mil', 'usgs.gov']
        if not any(test_email_addr.endswith(f'@{domain}') for domain in valid_domains):
            return jsonify({'error': 'Test email must be from @usace.army.mil or @usgs.gov'}), 400
        
        # Generate test CSV
        test_filename = f"test_rock_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        csv_content = generate_csv_results('{"grainCount": 15, "testData": true}', test_filename, test_email_addr)
        
        # Send test email
        success, message = send_email_with_csv(test_email_addr, csv_content, test_filename)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Test email sent successfully to {test_email_addr}',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test email failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Check if email credentials are set
    if EMAIL_PASSWORD == "your-app-password":
        print("WARNING: Please update EMAIL_PASSWORD in server.py with your CCA email app password")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
