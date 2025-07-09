import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
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
     
    try:
        bucket_name = os.environ.get("BUCKET_NAME")
        object_key = os.environ.get("OBJECT_KEY")  
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        pdf_content = response['Body'].read()
        if not pdf_content:
            raise ValueError("No content found in the PDF file.")
        return pdf_content
    
    except Exception as e:
        print(f"Error retrieving file from S3: {e}")
        return None
    

def format_msg(sender, requester):

    subject = f"{sender["name"]}'s Resume | Software/Cloud Engineering"
    body = f"""
            Hi {requester["name"]},
            
            Thank you for taking the time to review my resume. I appreciate your interest and the opportunity to be considered for a potential role.
            
            If there's any additional information or documentation you need—whether that's work samples, references, or clarification on anything in my experience, please don't hesitate to reach out.
            
            Feel free to reference my Github to view some of my projects! 
            ({sender["githubUrl"]})

            Looking forward to hearing from you.

            Best regards,  
            {sender["name"]}  
            {sender["phone"]}  
            {sender["linkedInUrl"]}
            """

    msg = MIMEMultipart()
    msg['From'] = sender["email"]
    msg['To'] = requester["email"]
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEApplication(get_resume_from_s3(), Name="Sami_Halwani_Resume.pdf")) 
    return msg

def send_email_with_attachment(sender, msg):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender["email"], os.environ.get("APP_PASSWORD"))
    server.send_message(msg)
    server.quit()


def lambda_handler(event, context):
    sender = os.environ.get("SENDER")
    requester = event["body"].get("requester")
    app_password = os.environ.get("APP_PASSWORD")

    try:
        msg = format_msg(sender, requester)
    except Exception as e:
        print(f"Error formatting message: {e}")
        return {
            'statusCode': 500,
            'body': 'Error formatting message.'
        }

    try:
        send_email_with_attachment (sender, msg)
    except Exception as e:
        print(f"Error sending email: {e}")
        return {
            'statusCode': 500,
            'body': 'Error sending email.'
        }

    return {
            'statusCode': 200,
            'body': 'Email with attachment sent successfully.'
            }