import boto3
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
env = os.getenv("ENV")
app = os.getenv("APP")
region = os.getenv("AWS_REGION")
filter_attribute = os.getenv("FILTER_ATTR")
retained_attribute_list = os.getenv("RETAINED_ATTR_LIST",'').split(',')
component_list = os.getenv("COMPONENT_LIST",'').split(',')
pra_components_list = os.getenv("PRA_COMPONENT_LIST",'').split(',')
ta_index = os.getenv("TA_INDEX")


# Initialize SSM client
ssm_client = boto3.client('ssm')

# Helper function to fetch parameters from Parameter Store
def get_parameter(parameter_name):
    try:
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Error retrieving parameter {parameter_name}: {str(e)}")
        raise

def process_grp_table(grp_table_name, region, filter_attribute, retained_attribute_list, component_list, pra_components_list):
    """
    Processes a DynamoDB table and returns a filtered Pandas DataFrame.

    Parameters:
        grp_table_name (str): DynamoDB table name.
        region (str): AWS region.
        filter_attribute (str): Attribute used for filtering (numeric value of string > 0).
        retained_attribute_list (list): Attributes to retain in the DataFrame.
        component_list (list): Attributes in the table used for further processing.
        pra_components_list (list): Practical components used for additional processing.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(grp_table_name)

    # Scan the entire table
    response = table.scan()
    items = response['Items']

    # Filter items based on the numeric value of the filter_attribute
    ##filtered_items = [
    ##    item for item in items
    ##    if filter_attribute in item and item[filter_attribute].isdigit() and int(item[filter_attribute]) > 0
    ##]

    filtered_items = [item for item in items if item.get(filter_attribute) != 'nan']

    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=retained_attribute_list + ['component', 'TtHr', 'Load', 'group', 'Instructor'])

    # Process each filtered item
    for item in filtered_items:
        ##filter_value = int(item[filter_attribute])
        filter_value = int(float(item[filter_attribute]))
        
        for groupnum in range(1, filter_value + 1):
            for component in component_list:
                if component in item and item[component].isdigit() and int(item[component]) > 0:
                    # Extract retained attributes
                    retained_data = {attr: item.get(attr, None) for attr in retained_attribute_list}

                    # Calculate TtHr
                    TtHr = int(item[component])

                    # Determine Load
                    if component in pra_components_list:
                        pra_pattern = item.get('Pra Pattern', None)
                        Load = str(TtHr / 2) if pra_pattern == 'Alt' else str(TtHr)
                    else:
                        Load = str(TtHr)

                    # Create a new row
                    new_row = {
                        **retained_data,
                        'component': component,
                        'TtHr': str(TtHr),
                        'Load': Load,
                        'group': groupnum,
                        'Instructor': "Unassigned"
                    }

                    # Append the row to the DataFrame
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    return df

def initialize_ta_table(input_df, ta_table_name, region):
    """
    Initializes a DynamoDB table by clearing its contents (if not empty) 
    and writing a Pandas DataFrame to it, ensuring all items are converted to strings.

    Parameters:
        input_df (pd.DataFrame): The DataFrame to write to the table.
        ta_table_name (str): Name of the DynamoDB table.
        region (str): AWS region.

    Returns:
        None
    """
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(ta_table_name)

    # Check if the table is empty
    response = table.scan()
    items = response.get('Items', [])

    # If the table is not empty, delete all items
    if items:
        print(f"Clearing {len(items)} items from {ta_table_name}.")
        with table.batch_writer() as batch:
            for item in items:
                # Use primary key(s) to delete items
                primary_keys = {key['AttributeName']: item[key['AttributeName']] for key in table.key_schema}
                batch.delete_item(Key=primary_keys)

    # Convert all DataFrame values to strings
    input_df = input_df.applymap(str)

    # Write the DataFrame to the DynamoDB table
    print(f"Writing {len(input_df)} records to {ta_table_name}.")
    with table.batch_writer() as batch:
        for _, row in input_df.iterrows():
            batch.put_item(Item=row.to_dict())

    print(f"Table {ta_table_name} has been initialized.")


if __name__ == "__main__":
    grp_table_name = get_parameter(f'/{app}/{env}/grp_table')
    ta_table_name = get_parameter(f'/{app}/{env}/ta_table')
    print(grp_table_name)

df = process_grp_table(grp_table_name, region, filter_attribute, retained_attribute_list, component_list, pra_components_list)

# Add TA index to the df
df[ta_index] = df.index + 1
initialize_ta_table(df, ta_table_name, region)
