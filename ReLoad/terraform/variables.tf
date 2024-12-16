variable "pref" {
  description = "Prefix for table names"
  type        = string
}

variable "env" {
  description = "Environment for table names"
  type        = string
}

variable "region" {
  description = "AWS region where the DynamoDB tables will be created"
  type        = string
}