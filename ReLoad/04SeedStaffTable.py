import boto3
import pandas as pd
from botocore.exceptions import ClientError

def write_xlsx_to_staff_table(file_path, sheet_name, target_table, region):
    """
    Reads an Excel sheet and writes the data to a DynamoDB table.

    Args:
        file_path (str): Path to the input Excel file.
        sheet_name (str): Name of the sheet in the Excel file to process.
        target_table (str): Name of the destination DynamoDB table.
        region (str): AWS region where the DynamoDB table resides.

    """
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(target_table)

    try:
        # Read the Excel sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Drop rows where all values are NaN
        df = df.dropna(how='all')

        # Iterate through each row and write to DynamoDB
        for _, row in df.iterrows():
            # Create a dictionary of non-empty attributes
            item = {col: str(row[col]) for col in df.columns if pd.notna(row[col])}

            # Ensure the 'total_load' attribute is set to '0' if empty
            if 'total_load' not in item or item['total_load'] == "":
                item['total_load'] = '0'

            # Add the 'taId' attribute
            item['taId'] = '0'

            # Write the item to the DynamoDB table
            table.put_item(Item=item)

        print(f"Data from {sheet_name} successfully written to {target_table}.")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except ValueError as ve:
        print(f"Error reading Excel file: {ve}")
    except ClientError as ce:
        print(f"DynamoDB Client Error: {ce.response['Error']['Message']}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


## Main program
write_xlsx_to_staff_table(
    file_path="/home/chao/Capability/Apr2025/TA_6510.xlsx",
    sheet_name="Staff",
    target_table="soe6510Stfdev",
    region="us-east-1"
)