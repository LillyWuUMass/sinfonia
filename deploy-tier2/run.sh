echo "Updating Helm repo"
helm repo update

echo -e "\n"

echo "Deploying Tier2 instances"
ansible-playbook deploy-tier2/deploy.yml -i deploy-tier2/inv.yaml -K
