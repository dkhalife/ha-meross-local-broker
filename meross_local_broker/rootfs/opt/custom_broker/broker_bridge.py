import datetime
import json
from meross_iot.model.enums import Namespace
from logger import get_logger
import ssl
from _md5 import md5
import paho.mqtt.client as mqtt
from threading import RLock
from db_helper import dbhelper
from model.enums import BridgeStatus
from protocol import _build_mqtt_message

APPLIANCE_SUBSCRIBE_TOPIC_PATTERN = '/appliance/%s/subscribe'
l = get_logger(__name__)


class BrokerDeviceBridge:
    def __init__(self,
                 broker,
                 device_uuid: str,
                 device_client_id: str,
                 device_mac: str,
                 user_id: str,
                 meross_key: str,
                 mqtt_server: str,
                 mqtt_port: int):

        self._l = RLock()
        self._broker_ref = broker
        self._connected = False
        self._uuid = device_uuid
        self._user_id = user_id
        self._hostname = mqtt_server
        self._port = mqtt_port
        self._username = device_mac
        self._key = meross_key
        md5_hash = md5()
        strtohash = f"{device_mac}{meross_key}"
        md5_hash.update(strtohash.encode("utf8"))
        pwdhash = md5_hash.hexdigest().lower()
        self._password = f"{user_id}_{pwdhash}"
        self._c = mqtt.Client(client_id=device_client_id, clean_session=True, protocol=mqtt.MQTTv311, transport="tcp")
        self._c.username_pw_set(username=self._username, password=self._password)

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        self._c.tls_set_context(context)

        self._c.on_connect = self._on_connect
        self._c.on_disconnect = self._on_disconnect
        self._c.on_message = self._on_message
        self._c.on_subscribe = self._on_subscribe
        self._c.on_disconnect = self._on_disconnect
        self._c.on_unsubscribe = self._on_unsubscribe

        self._errors_count = 0

    def start(self):
        self._c.connect(host=self._hostname, port=self._port)
        l.info("Starting bridged connection for uuid %s", self._uuid)
        self._c.loop_start()

    def stop(self):
        l.info("Terminating bridged connection for uuid %s", self._uuid)
        self._c.unsubscribe(topic=APPLIANCE_SUBSCRIBE_TOPIC_PATTERN % self._uuid)
        self._c.loop_stop(force=True)

    def _on_connect(self, client, userdata, rc, other):
        l.debug("Connected to Meross Iot network rc=%s", str(rc))
        self._connected = True

        # Subscribe to the remote Meross MQTT Broker
        client.subscribe(topic=APPLIANCE_SUBSCRIBE_TOPIC_PATTERN % self._uuid, qos=0)

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        l.debug("Subscribed to Meross MQTT topics.")
        dbhelper.update_device_bridge_status(device_uuid=self._uuid, status=BridgeStatus.CONNECTED)

        # Reset error counts as we finally established a successful connection
        self._errors_count = 0

        # TODO: Handle binding (re-issue binding message at every reconnection?)

    def _on_message(self, client, userdata, msg):
        # Forward the message to the local broker
        l.debug("Meross MQTT -> Device Bridge (%s), topic: %s, message: %s", self._uuid, str(msg.topic), str(msg.payload))
        self._broker_ref.forward_device_command_locally(topic=msg.topic, payload=msg.payload, originating_bridge_uuid=self._uuid)

    def _on_unsubscribe(self, *args, **kwargs):
        pass

    def _on_disconnect(self, client, userdata, rc):
        l.debug("Disconnected result code " + str(rc))
        self._connected = False
        dbhelper.update_device_bridge_status(device_uuid=self._uuid, status=BridgeStatus.DISCONNECTED)

        # If the client disconnected explicitly
        if rc == mqtt.MQTT_ERR_SUCCESS:
            l.info("Client has been disconnected successfully, RC: %s", str(rc))
            pass
        else:
            # Otherwise, if the disconnection was not intentional, we probably had a connection drop.
            l.error("Client has been disconnected. Connection will be re-attempted. Error code: %s", str(rc))
            self._errors_count += 1
            dbhelper.update_device_bridge_status(device_uuid=self._uuid, status=BridgeStatus.ERROR)
            # TODO: intercept wrong password and abort re-connection?

    def send_message(self, topic: str, payload: bytearray):
        with self._l:
            l.debug("Device Bridge (%s) -> Meross MQTT, topic: %s, message %s", self._uuid, str(topic), str(payload))
            r = self._c.publish(topic=topic, payload=payload)
