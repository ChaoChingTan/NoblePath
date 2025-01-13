import csv
import boto3
from botocore.exceptions import ClientError
import os
import random
import string
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
sender_email = os.getenv("SENDER_EMAIL")
file_path = os.getenv("CSVFILE")

def notify_new_users(status):
    """
    For newly created IAM users, sets console login password, forces password reset,
    and sends email notification with credentials and login URL.
    
    Args:
        status (dict): Dictionary with usernames and their creation status.
    """
    iam_client = boto3.client('iam')
    ses_client = boto3.client('ses')
    
    # Get the current AWS account alias for the sign-in URL
    account_alias = iam_client.list_account_aliases()['AccountAliases'][0]
    sign_in_url = f"https://{account_alias}.signin.aws.amazon.com/console"

    for user, msg in status.items():
        if msg == "User created successfully":
            # Generate a random password
            password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

            try:
                # Set the console login password and force password reset on first login
                iam_client.create_login_profile(
                    UserName=user,
                    Password=password,
                    PasswordResetRequired=True
                )
                
                # Compose the email
                email_subject = "Your AWS IAM User Credentials"
                email_body = f"""
                Hello {user},

                An IAM user account has been created for you. Below are your login details:

                Sign-In URL: {sign_in_url}
                Username: {user}
                Password: {password}

                Please use the provided credentials to log in and reset your password on first login.

                Best regards,
                Academy Admin Team
                """

                # Send email using SES
                ses_client.send_email(
                    Source=sender_email,
                    Destination={'ToAddresses': [user]},
                    Message={
                        'Subject': {'Data': email_subject},
                        'Body': {'Text': {'Data': email_body}}
                    }
                )
                print(f"Email sent to {user}")
            
            except ClientError as e:
                print(f"Failed to set login profile or send email for {user}: {e}")

def create_iam_users(users):
    """
    Creates IAM users if they do not already exist.
    The path and tag "Section" are based on the current working directory's folder name.
    
    Args:
        users (list): List of usernames to check/create.
        
    Returns:
        dict: Dictionary with usernames and their creation status.
    """
    iam_client = boto3.client('iam')
    
    # Get the current directory's folder name
    folder_name = os.path.basename(os.getcwd())
    path = f'/{folder_name}/'
    tag_key = "Section"
    
    result = {}

    for user in users:
        try:
            # Check if the user already exists
            iam_client.get_user(UserName=user)
            result[user] = "User already exists"
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # User does not exist, proceed to create
                try:
                    iam_client.create_user(
                        UserName=user,
                        Path=path,
                        Tags=[{'Key': tag_key, 'Value': folder_name}]
                    )
                    result[user] = "User created successfully"
                except ClientError as create_error:
                    result[user] = f"Failed to create user: {create_error}"
            else:
                result[user] = f"Error checking user: {e}"

    return result

def parse_csv_get_usernames(file_path):
    """
    Parses a CSV file and extracts all values under the 'Username' column.
    
    Args:
        file_path (str): Path to the CSV file.
    
    Returns:
        list: A list containing all 'Username' values.
    """
    users = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'Username' in row and row['Username']:  # Check if 'Username' exists and is not empty
                    users.append(row['Username'])
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return users

## Get the usernames from csv file
usernames = parse_csv_get_usernames(file_path)

## create the iam users if users do not already exist
status = create_iam_users(usernames)

##for user, msg in status.items():
##    print(f"{user}: {msg}")

## notify new users created via email
notify_new_users(status)
