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

# Setup MQTT connection params
MQTT_HOST=$(get_option 'host' '127.0.0.1')
MQTT_PORT=$(get_option 'port' '8883')
AGENT_USERNAME=$(get_option 'username' '')
AGENT_PASSWORD=$(get_option 'password' '')
CA_CERT=$(get_option 'ca_cert' '/data/ssl/ca.crt')

# Wait until mqtt is ready is available
bashio::log.info "Waiting MQTT server..."
bashio::net.wait_for $MQTT_PORT

exec python3 broker_agent.py --port $MQTT_PORT --host "$MQTT_HOST" --username "$AGENT_USERNAME" --password "$AGENT_PASSWORD" --cert-ca "$CA_CERT" $debug
