#!/usr/bin/with-contenv bashio
source /opt/utils/bashutils.sh
# ==============================================================================
# Configures Meross service
# ==============================================================================

DB_PATH=/data/database.db

# If the user has asked to reinit the db, remove it.
# Since we want to expose this functionality both from HA and Stand-Alone container,
# we need to fetch it also from HA
REINIT_DB=$(get_option 'reinit_db' 'false')
if [[ $REINIT_DB == "true" ]]; then
  if [[ -f $DB_PATH ]]; then
    bashio::log.warning "User configuration requires DB reinitialization. Removing previous DB data."
    rm $DB_PATH
  fi
fi

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