resource "aws_iam_user" "users" {
  for_each = var.users_map
  name     = each.key
  path     = "/${local.current_folder_name}/"
}

resource "aws_iam_group_membership" "group_membership" {
  for_each = var.users_map
  name     = "${each.value}_group_membership"
  users    = [each.key]
  group    = each.value
}