resource "aws_directory_service_directory" "siocorp_ad" {
  name     = "lucasquitman.fr"
  password = var.ad_password
  edition  = "Standard"
  type     = "MicrosoftAD"

  vpc_settings {
    vpc_id     = aws_vpc.siocorp-vpc.id
    subnet_ids = [aws_subnet.first-zone.id, aws_subnet.second-zone.id]
  }
}

resource "aws_subnet" "first-zone" {
  vpc_id            = aws_vpc.siocorp-vpc.id
  availability_zone = "eu-central-1a"
  cidr_block        = "172.16.1.0/24"
}

resource "aws_subnet" "second-zone" {
  vpc_id            = aws_vpc.siocorp-vpc.id
  availability_zone = "eu-central-1b"
  cidr_block        = "172.16.2.0/24"
}