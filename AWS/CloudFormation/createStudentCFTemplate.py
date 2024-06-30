import os
from dotenv import load_dotenv, find_dotenv
from jinja2 import Environment, FileSystemLoader

templateFile = 'iamUserTemplate.j2'

# Load environment variables from .env file
load_dotenv(find_dotenv('.env'))
load_dotenv(find_dotenv('.env.secret'))

# Load environment variables
group_name = os.getenv('GROUP_NAME', 'MyIAMGroup')
num_users = int(os.getenv('NUM_USERS', 1))
user_prefix = os.getenv('USERPREFIX','CFTuser')
init_pass = os.getenv('INITPASS')
##account_id = os.getenv('ACCOUNT_ID')

if not init_pass:
    raise ValueError("INITPASS environment variable is required")

# Set up Jinja2 environment
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

# Load the template
template = env.get_template(templateFile)

# Render the template with multiple environment variables
output = template.render(group_name=group_name, num_users=num_users, user_prefix=user_prefix, init_pass=init_pass)

print(output)