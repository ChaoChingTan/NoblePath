import os
import pandas as pd
import boto3
from dotenv import load_dotenv

def extract_fields_from_excel(file_path, sheet_name, fields=None):
    """
    Reads an Excel file, extracts specific fields from a specified sheet, 
    and returns a Pandas DataFrame. If fields are not provided, returns all fields.

    Parameters:
        file_path (str): Path to the .xlsx file.
        sheet_name (str): Name of the sheet to read.
        fields (list, optional): List of field names (columns) to extract. Default is None.

    Returns:
        pd.DataFrame: DataFrame containing the extracted fields.
    """
    try:
        # Read the specified sheet from the Excel file
        data = pd.read_excel(file_path, sheet_name=sheet_name)

        # If fields are provided, extract them; otherwise, return all fields
        if fields:
            missing_fields = [field for field in fields if field not in data.columns]
            if missing_fields:
                raise ValueError(f"Fields not found in the sheet: {missing_fields}")
            df = data[fields]
        else:
            df = data

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


    """
    Writes all items from a Pandas DataFrame to a DynamoDB table.

    Args:
        df (pd.DataFrame): The DataFrame containing data to write.
        table_name (str): The name of the DynamoDB table.
        region_name (str): The AWS region to connect to.
        row_attribute (str, optional): If provided, adds this attribute with the row number as the value.

    Returns:
        None
    """
    # Initialize the DynamoDB resource with the specified region
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(table_name)
    
    # Iterate over DataFrame rows
    for index, row in df.iterrows():
        item = row.to_dict()  # Convert the row to a dictionary
        if row_attribute:
            item[row_attribute] = index  # Add the row attribute with the row number
        # Write the item to the DynamoDB table
        table.put_item(Item=item)

def write_to_dynamodb(df, table_name, region_name, row_attribute=None):
    """
    Writes all items from a Pandas DataFrame to a DynamoDB table.

    Args:
        df (pd.DataFrame): The DataFrame containing data to write.
        table_name (str): The name of the DynamoDB table.
        region_name (str): The AWS region to connect to.
        row_attribute (str, optional): If provided, adds this attribute with the row number as the value.

    Returns:
        None
    """
    # Initialize the DynamoDB resource with the specified region
    dynamodb = boto3.resource('dynamodb', region_name=region_name)
    table = dynamodb.Table(table_name)
    
    # Replace NaN/NaT with None
    df = df.where(pd.notnull(df), None)
    
    # Convert numpy types to Python native types and handle special types
    def convert_value(value):
        if hasattr(value, 'item'):  # Handle numpy types
            return value.item()
        elif isinstance(value, pd.Timestamp):  # Convert Timestamp to ISO 8601 string
            return value.isoformat()
        elif isinstance(value, (int, float)):  # Convert numbers to strings
            return str(value)
        else:
            return value
    
    df = df.astype(object).applymap(convert_value)

    # Iterate over DataFrame rows
    for index, row in df.iterrows():
        item = row.to_dict()  # Convert the row to a dictionary
        # Filter out attributes with None values
        item = {k: v for k, v in item.items() if v is not None}
        
        if row_attribute:
            item[row_attribute] = str(index)  # Add the row attribute with the row number as a string
        
        # Write the item to the DynamoDB table
        table.put_item(Item=item)

def main():
    """
    Main function to read variables from the .env file and call the extractor function.
    """
    # Load environment variables from the .env file
    load_dotenv()

    # Get variables from the .env file
    file_path = os.getenv("EXCEL_FILE_PATH")
    sheet_name = os.getenv("EXCEL_SHEET_NAME")
    fields = os.getenv("EXCEL_FIELDS")

    if not file_path or not sheet_name:
        raise ValueError("Make sure EXCEL_FILE_PATH and EXCEL_SHEET_NAME are set in the .env file.")

    # Convert fields from a comma-separated string to a list, or leave as None
    fields = [field.strip() for field in fields.split(",")] if fields else None

    # Call the function to extract fields
    df = extract_fields_from_excel(file_path, sheet_name, fields)

    print("Extracted DataFrame:")
    print(df)

    table_name = os.getenv("TABLE_NAME")
    region_name = os.getenv("AWS_REGION")
    row_attribute = os.getenv("GRP_ID")

    write_to_dynamodb(df, table_name, region_name, row_attribute=row_attribute)

if __name__ == "__main__":
    main()
