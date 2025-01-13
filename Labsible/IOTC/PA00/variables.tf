variable "users_map" {
  type        = map(string)
  description = "Map of IAM users and their respective groups"
}

data "external" "folder_name" {
  program = ["./foldername.sh"]
}

locals {
  current_folder_name = data.external.folder_name.result.folder_name
}
