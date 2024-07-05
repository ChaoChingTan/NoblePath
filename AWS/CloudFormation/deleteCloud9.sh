#!/bin/bash

# Set the AWS region
REGION="ap-southeast-1"

# List all Cloud9 environment IDs in the specified region
environment_ids=$(aws cloud9 list-environments --region $REGION --query "environmentIds" --output text)

# Check if there are any environments to delete
if [ -z "$environment_ids" ]; then
  echo "No Cloud9 environments found in region $REGION."
  exit 0
fi

# Iterate over each environment ID and delete it
for env_id in $environment_ids; do
  echo "Deleting Cloud9 environment with ID: $env_id"
  aws cloud9 delete-environment --region $REGION --environment-id $env_id
done

echo "All Cloud9 environments in region $REGION have been deleted."