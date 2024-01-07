CONFIG_PATH=/data/options.json

function get_option {
    parameter_name=$1
    default_value=$2

    # Look if an env var is set for that parameter_name
    env_value=$(printenv "$parameter_name")
    if [[ $? -eq 0 ]]; then
        echo "$env_value"
    else
        echo "$default_value"
    fi
}