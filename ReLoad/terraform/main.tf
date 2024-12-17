provider "aws" {
  region = var.region
}

resource "aws_ssm_parameter" "grp_table_name" {
  name  = "/${var.app}/${var.env}/grp_table"
  type  = "String"
  value = aws_dynamodb_table.grp_table.name
}

resource "aws_dynamodb_table" "grp_table" {
  name         = "${var.pref}_GRP_${var.env}"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "grpId"
  range_key = "Section"

  attribute {
    name = "grpId"
    type = "S"
  }

  attribute {
    name = "Section"
    type = "S"
  }

#  lifecycle {
#    prevent_destroy = true
#  }
}

resource "aws_dynamodb_table" "ta_table" {
  name         = "${var.pref}_TA_${var.env}"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "Section"
  range_key = "taId"

  attribute {
    name = "Section"
    type = "S"
  }

  attribute {
    name = "taId"
    type = "S"
  }

#  lifecycle {
#    prevent_destroy = true
#  }
}

resource "aws_dynamodb_table" "stf_table" {
  name         = "${var.pref}_STF_${var.env}"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "staff"
  range_key = "taId"

  attribute {
    name = "staff"
    type = "S"
  }

  attribute {
    name = "taId"
    type = "S"
  }

  attribute {
    name = "acadsec"
    type = "S"
  }

  local_secondary_index {
    name            = "SectionIndex"
    projection_type = "ALL"

    range_key = "acadsec"
  }

#  lifecycle {
#    prevent_destroy = true
#  }
}

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
