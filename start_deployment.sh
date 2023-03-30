if [ -z "$1" ]
then
    echo "Usage - start_deployment <INSERT_COMPARTMENT_NAME>"
    echo "Usage - start_deployment <INSERT_COMPARTMENT_NAME> <INSERT_Deployment_NAME>"
    exit;
fi

# Assumes unique compartment name in tenancy. Adjust for duplicate compartment names
export compname=$1
export Compocid=`oci iam compartment list --compartment-id-in-subtree true --all |jq -r ".data[] | select(.name == \"${compname}\") | .id"`

if [ -z "$Compocid" ]
then
	echo "$compname not found"
	exit
fi

if [ ! -z "$2" ]
then
	export deploymentname=$2 
	export Deploymentocid=`oci goldengate deployment list --compartment-id $Compocid --all --query "data.items[?contains(\"display-name\",'$deploymentname')].id"|jq -r '.[]'`

else 

	# List Deployments and Status
	oci goldengate deployment list --compartment-id $Compocid --all --query 'data.items[*].{DeploymentName:"display-name",Status:"lifecycle-state"}' --output table
	echo "Enter Deployment Name to Start"
	read deploymentname
	export Deploymentocid=`oci goldengate deployment list --compartment-id $Compocid --all --query "data.items[?contains(\"display-name\",'$deploymentname')].id"|jq -r '.[]'`

fi 

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
