if [ -z $1 ]
then
	echo "Usage listgg_deployments.sh <compartment_name>" 
	exit
fi
export compname=$1
export Compocid=`oci iam compartment list --compartment-id-in-subtree true --all |jq -r ".data[] | select(.name == \"${compname}\") | .id"`
export query_text="query GoldenGateDeployment resources where compartmentID='$Compocid'"
oci search resource structured-search --query-text "$query_text" --query 'data.items[*].{DeploymentName:"display-name",Status:"lifecycle-state"}' --output table

