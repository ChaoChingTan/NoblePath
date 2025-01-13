import csv

csv_file = "users.csv"
tfvars_file = "terraform.tfvars"

users_map = {}

with open(csv_file, newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        username = row["username"].strip()
        group = row["group"].strip()
        users_map[username] = group

with open(tfvars_file, "w") as file:
    file.write('users_map = {\n')
    for user, group in users_map.items():
        file.write(f'  "{user}" = "{group}"\n')
    file.write('}\n')
