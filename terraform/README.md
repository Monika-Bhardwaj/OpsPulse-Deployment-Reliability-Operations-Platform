# OpsPulse AWS Infrastructure (Terraform)

This directory defines Infrastructure as Code (IaC) for provisioning the production VPC and Amazon EKS cluster for the OpsPulse DevSecOps platform.

## Architecture

- **VPC Module**: Custom VPC (`10.20.0.0/16`) across 2 Availability Zones (`ap-south-1a`, `ap-south-1b`).
  - 2 Public Subnets (`10.20.101.0/24`, `10.20.102.0/24`) with internet gateway for load balancers.
  - 2 Private Subnets (`10.20.1.0/24`, `10.20.2.0/24`) with NAT Gateway for secure worker nodes.
- **EKS Module**: Amazon EKS v1.31 cluster with managed worker node groups (`t3.medium`, 2-4 nodes).
- **Security**: Private subnet isolation, IAM least-privilege roles, cluster public endpoint access for management.

> ⚠️ **Cost Notice**: Running an EKS cluster and NAT Gateway incurs AWS charges (~$0.23/hr). Always run `terraform destroy` when not actively testing.

## Usage

```bash
# Initialize Terraform and download provider plugins
terraform init

# Validate syntax and configuration
terraform fmt
terraform validate

# Plan provisioning with custom variables
cp terraform.tfvars.example terraform.tfvars
terraform plan

# Apply infrastructure (Requires AWS credentials with EKS & VPC permissions)
terraform apply -auto-approve

# Configure kubectl to connect to the EKS cluster
aws eks update-kubeconfig --region ap-south-1 --name opspulse-eks

# Clean up all provisioned AWS resources
terraform destroy -auto-approve
```
