import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file

def create_dynamodb_table(
    table_name,
    partition_key_name,
    sort_key_name,
    partition_key_type='S',
    sort_key_type='S',
    lsi_name=None,
    lsi_sort_key_name=None,
    lsi_sort_key_type='S',
    projection_type='ALL',
    billing_mode='PAY_PER_REQUEST',
    region_name='us-east-1'
):
    """
    Creates a DynamoDB table with optional Local Secondary Index (LSI).

    Parameters:
        table_name (str): Name of the table to be created.
        partition_key_name (str): Name of the partition (hash) key.
        sort_key_name (str): Name of the sort (range) key for the main table.
        partition_key_type (str): Type of the partition key ('S' for string, 'N' for number, 'B' for binary). Default is 'N'.
        sort_key_type (str): Type of the sort key ('S', 'N', 'B'). Default is 'S'.
        lsi_name (str): Name of the Local Secondary Index. Default is None.
        lsi_sort_key_name (str): Name of the sort key for the LSI. Default is None.
        lsi_sort_key_type (str): Type of the LSI sort key ('S', 'N', 'B'). Default is 'S'.
        projection_type (str): Type of projection for the LSI ('ALL', 'KEYS_ONLY', 'INCLUDE'). Default is 'ALL'.
        billing_mode (str): Billing mode ('PAY_PER_REQUEST' or 'PROVISIONED'). Default is 'PAY_PER_REQUEST'.
        region_name (str): AWS region where the table should be created. Default is 'us-east-1'.

    Returns:
        dict: Information about the created table.
    """
    dynamodb = boto3.resource('dynamodb', region_name=region_name)

    # Define the attribute definitions
    attribute_definitions = [
        {'AttributeName': partition_key_name, 'AttributeType': partition_key_type},
        {'AttributeName': sort_key_name, 'AttributeType': sort_key_type}
    ]

    # Define the key schema
    key_schema = [
        {'AttributeName': partition_key_name, 'KeyType': 'HASH'},
        {'AttributeName': sort_key_name, 'KeyType': 'RANGE'}
    ]

    # Initialize optional LSI configuration
    local_secondary_indexes = []

    # Add LSI configuration if parameters are provided
    if lsi_name and lsi_sort_key_name:
        attribute_definitions.append(
            {'AttributeName': lsi_sort_key_name, 'AttributeType': lsi_sort_key_type}
        )
        local_secondary_indexes = [
            {
                'IndexName': lsi_name,
                'KeySchema': [
                    {'AttributeName': partition_key_name, 'KeyType': 'HASH'},
                    {'AttributeName': lsi_sort_key_name, 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': projection_type}
            }
        ]

    # Create the table
    table_params = {
        'TableName': table_name,
        'KeySchema': key_schema,
        'AttributeDefinitions': attribute_definitions,
        'BillingMode': billing_mode
    }

    if local_secondary_indexes:
        table_params['LocalSecondaryIndexes'] = local_secondary_indexes

    table = dynamodb.create_table(**table_params)

    # Wait until the table exists
    print(f"Creating table {table_name}...")
    table.wait_until_exists()
    print(f"Table {table_name} created successfully!")

    return table.meta.client.describe_table(TableName=table_name)

# Usage
if __name__ == "__main__":
    region_name = os.getenv("AWS_REGION", "us-east-1")
    table_name = os.getenv("TABLE_NAME", "DefaultTableName")
    partition_key_name = os.getenv("PARTITION_KEY_NAME", "DefaultPartitionKey")
    sort_key_name = os.getenv("SORT_KEY_NAME", "DefaultSortKey")

    table_info = create_dynamodb_table(
        table_name,
        partition_key_name,
        sort_key_name
    )
    
    print("Table Description:", table_info)
