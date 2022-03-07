# Create a VPC
resource "aws_vpc" "siocorp-vpc" {
  cidr_block = "172.16.0.0/16"
  tags = {
    Name = "siocorp-vpc"
  }
}
