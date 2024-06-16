#!/usr/bin/with-contenv bashio
source /opt/utils/bashutils.sh
pushd /opt/custom_broker >/dev/null

# Setup MQTT connection params
MQTT_HOST=$(get_option 'mqtt_host' '127.0.0.1')
MQTT_PORT=$(get_option 'mqtt_port' '8883')
CA_CERTS=$(get_option 'ca_certs' '')
DEBUG_PORT=$(get_option 'broker_debug_port' '')
AGENT_USERNAME=$(get_option 'username' '')
AGENT_PASSWORD=$(get_option 'password' '')

# Setup debug flag
DEBUG_MODE=$(get_option 'debug_mode' 'false')
if [[ $DEBUG_MODE == "true" ]]; then
  bashio::log.info "Starting broker agent with debug flag"
  debug_prefix="-m debugpy --listen 0.0.0.0:$DEBUG_PORT"
  debug_postfix="--debug"
else
  debug_prefix=""
  debug_postfix=""
fi

# Wait until mqtt is ready is available
bashio::log.info "Waiting MQTT server..."
bashio::net.wait_for $MQTT_PORT

exec python3 $debug_prefix broker_agent.py --port $MQTT_PORT --host "$MQTT_HOST" --username "$AGENT_USERNAME" --password "$AGENT_PASSWORD" --ca-certs "$CA_CERTS" $debug_postfix
