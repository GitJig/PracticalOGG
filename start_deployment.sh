export compname=JDBlog
export Compocid=`oci iam compartment list --compartment-id-in-subtree true --all |jq -r ".data[] | select(.name == \"${compname}\") | .id"`

# List Deployments and Status
oci goldengate deployment list --compartment-id $Compocid --all --query 'data.items[*].{DeploymentName:"display-name",Status:"lifecycle-state"}' --output table

echo "Enter Deployment Name to Start"
read deploymentname
export Deploymentocid=`oci goldengate deployment list --compartment-id $Compocid --all --query "data.items[?contains(\"display-name\",'$deploymentname')].id"|jq -r '.[]'`
if [ -z "$Deploymentocid" ]
then
	echo "Deployment $deploymentname not found in $compname"
	exit
else 
echo "Starting OCI GG Deployment $deploymentname"
fi

export WorkReqOCID=`oci goldengate deployment start --deployment-id $Deploymentocid |jq -r '."opc-work-request-id"'`

while true
do 
export status=`oci goldengate work-request get --work-request-id $WorkReqOCID|jq -r ".data.status"`
echo "OCI GoldenGate startup request for $deploymentname is -- $status"
if [ $status == "SUCCEEDED" ]
then	
	break
else
	sleep 20
fi
echo "Sleeping for 20 seconds"
echo "Ctrl-C to exit"
sleep 20
done 
