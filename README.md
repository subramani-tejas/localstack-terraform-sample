# localstack-terraform-sample

# overview
a Lambda function that writes to a DynamoDB table, 
orchestrated fully via Terraform against a LocalStack container.

## 1. /src/terraform

**provider.tf**
This is to bypass aws auth & route all AWS calls to localstack container

**main.tf**
provisions:
- the DynamoDB table,
- a dummy IAM role (required by Terraform's AWS provider, though LocalStack ignores IAM permissions by default), and
- the Lambda function payload.

## 2. /src/app

**app.py**
The Lambda script. Because LocalStack transparently handles AWS SDK requests inside its local Lambda execution environment, you do not need to inject custom endpoints in your application code. This keeps it identical to your production build.

## 3. Execution Workflow
With your docker-compose up -d already running, execute these commands from the directory containing your Terraform files:

Bash
### 1. Initialize Terraform
``` terraform init ```

### 2. Provision the resources on LocalStack
``` terraform apply -auto-approve ```

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
