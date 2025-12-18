terraform {
  required_providers {
    qdrant = {
      source = "qdrant/qdrant-cloud"
    }
  }
}

variable "api_key" {
  type = string
  sensitive = true
}

provider "qdrant" {
  api_key = var.api_key
}

variable "cluster_name" {
  type = string
}

variable "cloud_provider" {
  type    = string
  default = "aws"
}

variable "cloud_region" {
  type    = string
  default = "us-east-1"
}

variable "cluster_configuration" {
  type = object({
    num_nodes = number
    node_config = object({
        resource_id = string
    })
  })
}

resource "qdrant_cloud_accounts_cluster" "cluster" {
  name           = var.cluster_name
  cloud_provider = var.cloud_provider
  cloud_region   = var.cloud_region
  
  configuration {
    node_configuration {
        package_id = var.cluster_configuration.node_config.resource_id
    }
    number_of_nodes = var.cluster_configuration.num_nodes
  }
}

output "cluster_id" {
  value = qdrant_cloud_accounts_cluster.cluster.id
}

output "cluster_endpoint" {
  value = qdrant_cloud_accounts_cluster.cluster.url
}

output "api_key" {
    value = qdrant_cloud_accounts_cluster.cluster.api_key
    sensitive = true
}

