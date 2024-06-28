## Example Usage

To create CloudFormation Stack

```bash
aws cloudformation create-stack --stack-name singleIAMUser --capabilities CAPABILITY_NAMED_IAM --template-body file://singleIAMUser.yml
```

To delete stack

```bash
aws cloudformation delete-stack --stack-name singleIAMUser
```