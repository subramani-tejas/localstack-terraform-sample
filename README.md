# localstack-terraform-sample

# Overview
A Lambda function that writes to a DynamoDB table, 
orchestrated fully via Terraform against a LocalStack container.

## 1. /src/terraform

### provider.tf

This is to bypass AWS authentication/authorization & route all AWS calls to localstack container.

### main.tf

provisions:
- the DynamoDB table,
- a dummy IAM role (required by Terraform's AWS provider, though LocalStack ignores IAM permissions by default), and
- the Lambda function payload.

## 2. /src/app

### app.py

The Lambda script. Because LocalStack transparently handles AWS SDK requests inside its local Lambda execution environment, you do not need to inject custom endpoints in your application code. This keeps it identical to your production build.

## 3. Execution Workflow

With your `docker-compose up -d` already running, execute these commands from the directory containing your Terraform files:

### 1. Initialize Terraform
``` terraform init ```

### 2. Provision the resources on LocalStack
``` terraform apply ```

### 3. Invoke the Lambda function locally
```
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name WriteEvent \
    --payload '{"payload": "Testing LocalStack integration"}' \
    --cli-binary-format raw-in-base64-out \
    response.json
```

### 4. Verify the record was successfully written to DynamoDB
```
aws --endpoint-url=http://localhost:4566 dynamodb scan \
    --table-name local-events
```

Note: If Terraform fails to provision the IAM role, ensure your docker-compose.yml includes iam in the SERVICES list. Alternatively, remove the SERVICES variable entirely, as modern LocalStack versions handle all core services natively on port 4566 without strict scoping.

## 4. Terraform debugging

A known state-mismatch issue. You might hit an infinite polling loop caused by an incompatibility between 6.13.0 Terraform AWS provider and LocalStack, such as how it verifies DynamoDB table creation by waiting for specific API attributes like WarmThroughput.Status in the response. 

Because LocalStack's local API simulator doesn't natively return these exact fields, Terraform loops continuously, assuming the table is still provisioning, and eventually gives up after 21 retries.  

Here is the fix: Pin your AWS provider version. Downgrade to the last known stable version for DynamoDB on LocalStack (6.12.0) in `provider.tf`.

Additionall, purge the tainted tfstate. Because the previous Terraform run failed mid-creation, your local state file is now poisoned and will block further applies. 

Clean the directory and re-initialize:
```bash
rm -rf .terraform terraform.tfstate terraform.tfstate.backup .terraform.lock.hcl
terraform init
terraform apply -auto-approve
```