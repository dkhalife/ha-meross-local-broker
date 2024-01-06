#!/usr/bin/with-contenv bashio

CONFIG_PATH=/data/options.json

pushd /opt/custom_broker >/dev/null
source /opt/utils/bashutils.sh

# Setup debug flag
DEBUG_MODE=$(get_option 'debug_mode' 'false')
if [[ $DEBUG_MODE == "true" ]]; then
  bashio::log.info "Starting broker agent with debug flag"
  debug="--debug"
else
  debug=""
fi

# Wait until mqtt is ready is available
bashio::log.info "Waiting MQTT server..."
bashio::net.wait_for 2001

exec python3 broker_agent.py --port 2001 --host localhost --username "$AGENT_USERNAME" --password "$AGENT_PASSWORD" --cert-ca "/data/mqtt/certs/ca.crt" $debug
