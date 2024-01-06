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

# Generate a random password for agent user
AGENT_USERNAME="_agent"
AGENT_PASSWORD=$(openssl rand -base64 32)
AGENT_PBKDF2=$(/usr/share/mosquitto/pw -p $AGENT_PASSWORD)
echo "$AGENT_USERNAME:$AGENT_PBKDF2">/etc/mosquitto/auth.pw

# Wait until mqtt is ready is available
bashio::log.info "Waiting MQTT server..."
bashio::net.wait_for 2001

exec python3 broker_agent.py --port 2001 --host localhost --username "$AGENT_USERNAME" --password "$AGENT_PASSWORD" --cert-ca "/data/mqtt/certs/ca.crt" $debug
