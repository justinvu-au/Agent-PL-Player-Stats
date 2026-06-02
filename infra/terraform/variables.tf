variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "australiaeast"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "pl-stats-rg"
}

variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "plstats"
}

variable "acr_name" {
  description = "Azure Container Registry name (must be globally unique, alphanumeric only)"
  type        = string
  default     = "plstatsacr"
}

variable "aks_node_count" {
  description = "Number of AKS nodes"
  type        = number
  default     = 1
}

variable "aks_node_size" {
  description = "AKS node VM size"
  type        = string
  default     = "Standard_D2s_v3"
}