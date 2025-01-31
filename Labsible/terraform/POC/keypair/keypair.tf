provider "aws" {
  region = "ap-southeast-1"
}

resource "tls_private_key" "labkey" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "private_key" {
  content  = tls_private_key.labkey.private_key_pem
  filename = "${path.module}/labkey.pem"
  file_permission = "0600"
}

resource "aws_key_pair" "labkey" {
  key_name   = "labkey"
  public_key = tls_private_key.labkey.public_key_openssh
}
