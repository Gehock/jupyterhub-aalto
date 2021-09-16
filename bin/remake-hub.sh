SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
NAMESPACE=${1:-jupyter-test}
echo "Namespace: $NAMESPACE"

# Syntax check the hub config file first.
if ! python3 -m py_compile $SCRIPTPATH/../jupyterhub_config.py ; then
    echo "jupyterhub_config.py has invalid syntax, aborting the hub restart."
    exit
fi

$SCRIPTPATH/delete-hub.sh $NAMESPACE
# sometimes this proxy pid needs deletion... eventually find a better solution.
if [ "$NAMESPACE" = "jupyter" ]; then
    rm -f /mnt/jupyter/admin/hubdata/jupyterhub-proxy.pid
elif [ "$NAMESPACE" = "jupyter-test" ]; then
    rm -f /mnt/jupyter/jupyter-test/admin/hubdata/jupyterhub-proxy.pid
fi

$SCRIPTPATH/create-hub.sh $NAMESPACE
