module "network" {
  source      = "./modules/network"
  name_prefix = terraform.workspace == "default" ? "rag-supply" : "rag-supply-${terraform.workspace}"
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "public_subnet_ids" {
  value = module.network.public_subnet_ids
}
