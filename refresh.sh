#!/usr/bin/env bash

set -e

#runs=( ea9e64a4-c8b6-4b0a-8abf-d7786647e016 2b967d44-542e-4c7a-9dc8-ac0944e572ad f9802af1-c338-40c1-8809-3e0597a63aa2 f0180ffd-55b2-4989-91b0-0e33d21ad3fc  )
runs=( f9802af1-c338-40c1-8809-3e0597a63aa2 f0180ffd-55b2-4989-91b0-0e33d21ad3fc  )

for run in "${runs[@]}" ; do 
	echo -n "Fetching logs for ${run} ..."
	./cromshell fetch-logs ${run} &> /dev/null
	echo -e "\tDone"
done

./cromshell list -c -u

echo

echo "Tool logs can be found here:"
for run in "${runs[@]}" ; do 
	echo "    /Users/jonn/.cromshell/cromwell-v36.dsde-methods.broadinstitute.org/${run}/call-Funcotate/Funcotate.log"
done

echo 
for run in "${runs[@]}" ; do 
	echo -n " /Users/jonn/.cromshell/cromwell-v36.dsde-methods.broadinstitute.org/${run}/call-Funcotate/Funcotate.log"
done
echo

