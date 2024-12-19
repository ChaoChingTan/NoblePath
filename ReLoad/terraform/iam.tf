
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
  name = "${var.env}grouping"
  path = "/${var.app}/${var.env}/"
}

resource "aws_iam_group_membership" "grouping_membership" {
  name  = "grouping_membership"
  group = aws_iam_group.grouping.name
  users = [aws_iam_user.grouping_user.name]
}
