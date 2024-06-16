#!/usr/bin/with-contenv bashio
source /opt/utils/bashutils.sh
pushd /opt/custom_broker >/dev/null

# Setup MQTT connection params
HTTPS_HOST=$(get_option 'https_host' '127.0.0.1')
HTTPS_PORT=$(get_option 'https_port' '443')
CA_CERT=$(get_option 'https_cert' '')
CA_KEY=$(get_option 'https_key' '')
DEBUG_PORT=$(get_option 'api_debug_port' '')

# Setup debug flag
DEBUG_MODE=$(get_option 'debug_mode' 'false')
if [[ $DEBUG_MODE == "true" ]]; then
  bashio::log.info "Starting flask with debug flag"
  debug_prefix="-m debugpy --listen 0.0.0.0:$DEBUG_PORT"
  debug_postfix="--debug"
else
  debug_prefix=""
  debug_postfix=""
fi

# Start flask
bashio::log.info "Starting flask..."
bashio::net.wait_for $HTTPS_PORT

exec python3 $debug_prefix ./http_api.py --port $HTTPS_PORT --host "$HTTPS_HOST" --cert-ca "$CA_CERT" --cert-key "$CA_KEY" $debug_postfix
