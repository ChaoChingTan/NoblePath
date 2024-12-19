variable "pref" {
  description = "Prefix for table names"
  type        = string
}

variable "env" {
  description = "Environment"
  type        = string
}

variable "region" {
  description = "AWS region where the DynamoDB tables will be created"
  type        = string
}

variable "app" {
  description = "Application name"
  type        = string
}

#variable "user_count" {
#  description = "Number of users to create"
#  type = number
#  default = 2
#}

variable "iam_users_grouping" {
  type = list(object({
    username = string
  }))
}