#!/usr/bin/with-contenv bashio
source /opt/utils/bashutils.sh
# ==============================================================================
# Configures Meross service
# ==============================================================================

DB_PATH=/data/database.db

# Initializing DB
pushd /opt/custom_broker >/dev/null

bashio::log.info "Setting up the database in $DB_PATH"
python3 setup.py

if [[ $? -ne 0 ]]; then
  bashio::log.error "Error when setting up the database file. Aborting."
  exit 1
else
  bashio::log.info "DB setup finished"
fi
popd >/dev/null

# Prepare log dir
mkdir -p /var/log/api
chown nobody:nogroup /var/log/api
chmod 02755 /var/log/api