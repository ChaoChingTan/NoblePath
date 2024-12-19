
resource "aws_iam_policy" "grp_table_readonly" {
  name        = "grp_table_readonly_policy"
  description = "IAM policy for readonly access to grp_table"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = [
          "dynamodb:DescribeTable",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Effect   = "Allow",
        Resource = aws_dynamodb_table.grp_table.arn
      },
      {
        "Action": [
          "dynamodb:DescribeTable",
          "dynamodb:ListTables"
        ],
        "Effect": "Allow",
        "Resource": "*",
        "Condition": {
          StringEquals: {
            "aws:RequestedRegion": [
              "ap-southeast-1"
            ]
          }
        }
      }
    ]
  })
}

resource "aws_iam_group" "grouping" {
  name = "${var.env}grouping"
  path = "/${var.app}/${var.env}/"
}

resource "aws_iam_group_policy_attachment" "grouping_policy_attach" {
  group      = aws_iam_group.grouping.name
  policy_arn = aws_iam_policy.grp_table_readonly.arn
}

resource "aws_iam_user" "grouping_user" {
  for_each = { for user in var.iam_users_grouping : user.username => user }
  name = "${var.env}${each.key}"
  path = "/${var.app}/${var.env}/"
}

# Create login profile for the users to enable console access
resource "aws_iam_user_login_profile" "login_grouping" {
  for_each           = { for user in var.iam_users_grouping : user.username => user }
  user               = aws_iam_user.grouping_user[each.key].name
  password_reset_required = true
}

resource "aws_iam_group_membership" "grouping_membership" {
  name  = "grouping_membership"
  group = aws_iam_group.grouping.name
  users = [for user in aws_iam_user.grouping_user : user.name]
}
