# Automated Resume Delivery via AWS Lambda & API Gateway

This project is a fully automated infrastructure and deployment pipeline for serving resumes via a secured API. It uses AWS Lambda, API Gateway, and S3 - all provisioned via CloudFormation - and automatically deployed via GitHub Actions.

---

## Project Overview

This infrastructure allows you to:

- Upload a resume file to S3 via GitHub Actions
- Zip and deploy backend Lambda logic automatically
- Expose a POST API at `/resume` secured by an API Key
- Update code and infrastructure with every push to `main`

---

## Tech Stack

- **AWS CloudFormation** – Infrastructure as code (S3, Lambda, API Gateway, IAM)
- **AWS Lambda** – Python backend logic to serve your resume
- **API Gateway** – Public endpoint for clients to request the resume
- **S3** – Storage for your resume file and Lambda package
- **GitHub Actions** – Automated CI/CD pipeline for deploying infrastructure and code

---

##  Project Structure
<pre> ```. ├── .github/ │ └── workflows/ │ └── deploy.yaml # CI/CD pipeline ├── cloudformation/ │ ├── createS3Bucket.yaml # CFN template to provision S3 bucket │ └── lambda-apigateway.yaml # CFN template to provision Lambda + API Gateway ├── code/ │ └── index.py # Lambda function entry point ├── pdfs/ │ └── your_resume.pdf # Resume to be uploaded to S3 ``` </pre>

##  Deployment Workflow (CI/CD)

On every `push` to the `main` branch, GitHub Actions will:

1. **Validate** the CloudFormation templates.
2. **Check if the S3 bucket exists** — if not, it creates it.
3. **Zip the Lambda code** in `code/` directory.
4. **Upload**:
   - `lambda.zip` → `s3://<your-bucket>/code/lambda.zip`
   - Resume file → `s3://<your-bucket>/pdfs/`
5. **Check if the Lambda function exists**:
   - If not: deploy full infra via CloudFormation.
   - If yes: skip infra deploy and just update the Lambda code.
6. **Print the deployed API endpoint** and API Key in the logs.

---

## Secrets Required in GitHub Actions

| Secret Name              | Description |
|--------------------------|-------------|
| `AWS_ACCESS_KEY_ID`      | IAM access key with CloudFormation, Lambda, S3 permissions |
| `AWS_SECRET_ACCESS_KEY`  | IAM secret key |
| `AWS_REGION`             | AWS region (e.g., `us-west-2`) |
| `S3_BUCKET_NAME`         | Target bucket name (must match CFN param) |
| `RESUME_NAME`            | Filename of your resume (e.g., `pdfs/my_resume.pdf`) |
| `LAMBDA_FUNCTION_NAME`   | Logical name of the Lambda function (e.g., `AutomatedResumeFunction`) |

---

## Lambda Handler

```python
# code/index.py

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Resume available at https://your-bucket.s3.amazonaws.com/pdfs/<your-file.pdf>"
    }
```
Customize this function to dynamically fetch metadata, serve signed URLs, or trigger resume downloads.

## API Gateway Endpoint
Once deployed, your API will be available at: https://<api-id>.execute-api.<region>.amazonaws.com/prod/resume

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/resume \
  -H "x-api-key: YOUR_API_KEY"
```

## Cloudformation Outputs
The deployment will print:
- LambdaFunctionArn
- ApiGatewayUrl
- ApiKey

## License
MIT License. Use this as a boilerplate for your own resume, portfolio, or document-serving automation.