#!/usr/bin/env python3
"""
Test script to send a draft example email to verify email configuration
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import csv
import io
from datetime import datetime

# Email configuration (same as server.py)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = "pratt@cca.edu"
EMAIL_PASSWORD = "thiigjismzexedub"  # App password (should be exactly 16 chars)

def generate_test_csv():
    """Generate a test CSV file with sample data"""
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
    
    # Test data row
    test_row = [
        f"SPK_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        datetime.now().isoformat(),
        "william.a.pratt@usace.army.mil",  # Your test email
        "test_rock_sample.jpg",
        "25",
        "2.5",
        "1.8", 
        "45.2",
        "This is a test CSV generated to verify email functionality"
    ]
    
    # Write CSV
    writer = csv.writer(csv_output)
    writer.writerow(headers)
    writer.writerow(test_row)
    
    return csv_output.getvalue()

def send_test_email():
    """Send a test email with CSV attachment"""
    
    # IMPORTANT: Change this to your test email address
    # Use your actual USACE or USGS email for testing
    TEST_RECIPIENT = "william.a.pratt@usace.army.mil"  # Your USACE email
    
    print(f"Preparing to send test email to: {TEST_RECIPIENT}")
    print(f"From: {EMAIL_USERNAME}")
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = TEST_RECIPIENT
        msg['Subject'] = f"TEST: SPK Rock Sample Analysis Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Email body
        body = f"""
Dear Test User,

This is a TEST EMAIL to verify the SPK Analysis System email configuration.

This is NOT a real rock sample analysis - this is just a test to make sure:
- Email configuration is working
- CSV generation works properly
- SMTP connection is successful

Test Details:
- Analysis ID: SPK_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}
- Timestamp: {datetime.now().isoformat()}
- This is a generated test CSV file

Please find the test CSV file attached.

Best regards,
USACE Sacramento District - SPK Analysis System
Sent from: pratt@cca.edu

---
This is a test email. Please ignore if received.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Generate test CSV
        csv_content = generate_test_csv()
        
        # Attach CSV file
        csv_filename = f"SPK_TEST_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(csv_content.encode('utf-8'))
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename= {csv_filename}')
        msg.attach(attachment)
        
        print("Connecting to SMTP server...")
        
        # Connect and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        print(f"Logging in as {EMAIL_USERNAME}...")
        print(f"Password length: {len(EMAIL_PASSWORD)} characters")
        print(f"Password: {'*' * len(EMAIL_PASSWORD)}")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        print("Sending email...")
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, TEST_RECIPIENT, text)
        server.quit()
        
        print("✅ SUCCESS! Test email sent successfully!")
        print(f"📧 Email sent from: {EMAIL_USERNAME}")
        print(f"📧 Email sent to: {TEST_RECIPIENT}")
        print(f"📎 CSV attachment: {csv_filename}")
        
        return True, "Test email sent successfully"
        
    except Exception as e:
        error_msg = f"❌ FAILED to send test email: {str(e)}"
        print(error_msg)
        
        # Additional troubleshooting info
        if "BadCredentials" in str(e):
            print("\n🔍 Troubleshooting BadCredentials error:")
            print("1. Make sure 2-Step Verification is enabled")
            print("2. Verify the app password was generated for 'Mail'")
            print("3. Check if 'Less secure app access' is needed")
            print("4. Try regenerating the app password")
            print("5. Confirm pratt@cca.edu is a Google Workspace account")
        
        return False, error_msg

if __name__ == "__main__":
    print("🧪 SPK Email Configuration Test")
    print("=" * 40)
    
    # Check configuration
    if EMAIL_PASSWORD == "your-app-password":
        print("⚠️  WARNING: You need to update EMAIL_PASSWORD with your actual app password")
        exit(1)
    
    # Run test
    success, message = send_test_email()
    
    if success:
        print("\n🎉 Email test completed successfully!")
        print("Check your test email inbox for the message with CSV attachment.")
    else:
        print(f"\n💥 Email test failed: {message}")
        print("\nTroubleshooting tips:")
        print("- Verify your app password is correct")
        print("- Check if 2-factor authentication is enabled")
        print("- Ensure SMTP settings are correct for Google Workspace")
