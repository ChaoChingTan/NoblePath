provider "aws" {
  region = "us-east-1"
}

# Create IAM groups (convert list to set using toset())
resource "aws_iam_group" "groups" {
  for_each = toset(distinct([for user, group in var.users_map : group]))
  name     = each.value
}

# Create IAM users with the path set to the group name
resource "aws_iam_user" "users" {
  for_each = var.users_map
  name     = each.key
  path     = "/${each.value}/"
}

# Attach users to groups
resource "aws_iam_group_membership" "group_membership" {
  for_each = var.users_map
  name     = "${each.value}_group_membership"
  users    = [each.key]
  group    = aws_iam_group.groups[each.value].name
}
