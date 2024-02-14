# Alpha release 0.2 OCI GG Topology Viewer

Requires Python 3.8 or higher.
Tested with Python 3.11.2

How to use?

#Command to generate OCI GG output in json format

oci goldengate trail-file-summary list-trail-files --deployment-id <deployment_ocid> > outputfile.json


python ggtopo.py
Provide valid OCI GG CLI output in .json format generate from CLI command above.  

Access the topology diagram from 127.0.0.1:7079 

Change port from 7079 in the script if required. 

# change port here
   app.run(debug=True,port=7079)

   