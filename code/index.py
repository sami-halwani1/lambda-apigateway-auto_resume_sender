import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import json
import os
import boto3


"""
Project Name: Lambda + API Gateway Email Sender
Description:
The Purpose of this Lambda Function is to send an email to recruiters who request a copy of Sami Halwani's resume.
This function is triggered by an API Gateway event, which contains the receiver's email address.

The function will pull Sami's Resume from an S3 bucket, attach it to the email, and send it to the receiver's email address.
The function uses the AWS Lambda environment variables to get the sender's email, and the Gmail SMTP app password.

Author: Sami Halwani
Date: 07/08/2025

"""


def get_resume_from_s3():
    s3 = boto3.client('s3')
    bucket_name = os.environ.get("BUCKET_NAME")
    object_key = os.environ.get("OBJECT_KEY") 

    if not bucket_name or not object_key:
        raise ValueError("Missing S3 bucket or object key in environment variables.") 
     
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        return response['Body'].read()
    
    except Exception as e:
        print(f"Error retrieving file from S3: {e}")
        return None
    

def format_msg(sender, requester):

    subject = f"{sender['name']}'s Resume | Software/Cloud Engineering"
    body = f"""
        Hi {requester['name']},
                
        Thank you for taking the time to review my resume. I appreciate your interest and the opportunity to be considered for a potential role.
        
        If there's any additional information or documentation you need—whether that's work samples, references, or clarification on anything in my experience, please don't hesitate to reach out.
        
        Feel free to reference my Github to view some of my projects! 
        ({sender["githubUrl"]})

        Looking forward to hearing from you.

        Best regards,  
        {sender['name']}  
        {sender['phone']}  
        {sender['linkedInUrl']}
        """

    msg = MIMEMultipart()
    msg['From'] = sender['email']
    msg['To'] = requester['email']
    msg['Reply-To'] = sender["email"]
    msg['X-Priority'] = '1'
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    resume_data = get_resume_from_s3()
    if resume_data:
        msg.attach(MIMEApplication(resume_data, Name=f"{sender['name']}_Resume.pdf")) 
    else:
        print("Warning: Resume could not be retrieved from S3.")

    return msg

def send_email_with_attachment(sender, msg):
    app_password = os.environ.get("APP_PASSWORD")
    if not app_password:
        raise ValueError("Missing APP_PASSWORD environment variable.")
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        server.starttls()
        server.login(sender["email"], app_password)
        server.send_message(msg)
    finally:
        server.quit()


def lambda_handler(event, context):
    sender_str = os.environ.get("SENDER")
    print(sender_str)
    sender = json.loads(sender_str)
    requester = {}

    for record in event['Records']:
        new_image = record['dynamodb']
        try:
            body = new_image["NewImage"]
            requester['name'] = body.get('name').get('S')
            requester['email'] = body.get('email').get('S')
        except Exception as e:
            print(f"Error extracting requester information: {e}")
            return {"statusCode": 400, "body": "Invalid requester information."}
        try:
            msg = format_msg(sender, requester) 
            send_email_with_attachment (sender, msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
            return {
                'statusCode': 500,
                'body': 'Error formatting message.'
            }
        
    # try:
    #     body = json.loads(event.get("body", "{}"))
    #     requester = body.get("requester")
    #     if not requester:
    #         raise ValueError("Requester information is missing in the request body.")
    # except Exception as e:
    #     print(f"Invalid request body: {e}")
    #     return {"statusCode": 400, "body": "Invalid request format."}
    
    # try:
    #     msg = format_msg(sender, requester) 
    #     send_email_with_attachment (sender, msg)
    # except Exception as e:
    #     print(f"Failed to send email: {e}")
    #     return {
    #         'statusCode': 500,
    #         'body': 'Error formatting message.'
    #     }

    return {
            'statusCode': 200,
            'body': 'Email with attachment sent successfully.'
            }