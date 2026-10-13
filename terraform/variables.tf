variable "aws_region" {
  description = "AWS region for provisioning OpsPulse infrastructure"
  type        = string
  default     = "ap-south-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "The aws_region must be a valid AWS region format (e.g., ap-south-1, us-east-1)."
  }
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "opspulse-eks"

  validation {
    condition     = length(var.cluster_name) >= 3 && length(var.cluster_name) <= 40
    error_message = "The cluster_name must be between 3 and 40 characters long."
  }
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for OpsPulse VPC"
  type        = string
  default     = "10.20.0.0/16"
}
