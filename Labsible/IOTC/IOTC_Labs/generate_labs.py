import os
from jinja2 import Environment, FileSystemLoader
import yaml

# Define directories
TEMPLATE_DIR = "templates"
VARS_DIR = "vars"
OUTPUT_DIR = "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load Jinja environment
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# Iterate over variable files
for var_file in os.listdir(VARS_DIR):
    if var_file.endswith(".yml"):
        week_name = var_file.replace(".yml", "")  # Extract "week1", "week2", etc.
        
        # Load variables from YAML file
        with open(os.path.join(VARS_DIR, var_file)) as f:
            variables = yaml.safe_load(f)

        # Determine which template to use (specific or general)
        template_name = f"{week_name}_lab.j2" if f"{week_name}_lab.j2" in os.listdir(TEMPLATE_DIR) else "general_lab.j2"
        template = env.get_template(template_name)

        # Render and save output
        output_text = template.render(variables)
        output_file = os.path.join(OUTPUT_DIR, f"{week_name}_lab.txt")
        
        with open(output_file, "w") as f:
            f.write(output_text)
        
        print(f"Generated: {output_file}")

print("Lab instructions for all weeks have been generated successfully!")
