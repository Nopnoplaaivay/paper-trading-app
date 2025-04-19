import requests
import time
import urllib3
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTv5

from src.cache.shared_state import MESSAGE_QUEUE
from src.common.consts import DNSEConsts
from src.cache.config import DNSEConfigs
from src.modules.base.repositories import BaseRepo
from src.utils.logger import LOGGER

import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = os.getenv("DNSE_USERNAME")
PASSWORD = os.getenv("DNSE_PASSWORD")

MQTT_TOPICS = [
    (DNSEConfigs.TOPIC_STOCK_INFO + "/+", 0),
    (DNSEConfigs.TOPIC_TICK + "/+", 0),
    (DNSEConfigs.TOPIC_OHLC_1M + "/+", 0),
    (DNSEConfigs.TOPIC_SESSION + "/+", 0)
]

class DNSEMqtt:
    topic: str = None
    repo: BaseRepo
    client: mqtt_client.Client = None
    FLAG_EXIT: bool = False
    loop = None

    @classmethod
    def run(cls):
        """Setup the MQTT client"""
        investor_id, token = cls.get_account_info()
        cls.client = mqtt_client.Client(
            DNSEConsts.CLIENT_ID, protocol=MQTTv5, transport="websockets"
        )
        cls.client.username_pw_set(investor_id, token)
        cls.client.tls_set_context()
        cls.client.ws_set_options(path="/wss")
        cls.client.on_connect = cls.on_connect
        cls.client.on_message = cls.on_message
        cls.FLAG_EXIT = False

        try:
            cls.connect_mqtt()
            cls.client.loop_forever()
        except KeyboardInterrupt:
            LOGGER.info("Exiting...")

    @classmethod
    def get_account_info(cls):
        """Get token"""
        login_url = "https://services.entrade.com.vn/dnse-auth-service/login"
        payload = {"username": USERNAME, "password": PASSWORD}
        try:
            res = requests.post(login_url, json=payload, verify=False)
            data = res.json()
            token = data.get("token")
        except Exception as e:
            raise Exception(f"Failed to get token: {e}")

        """Get investor_id"""
        investor_info_url = "https://services.entrade.com.vn/dnse-user-service/api/me"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.get(investor_info_url, headers=headers, verify=False)
            data = res.json()
            investor_id = data.get("investorId")
        except Exception as e:
            raise Exception(f"Failed to get investor_id: {e}")

        return investor_id, token

    @classmethod
    def connect_mqtt(cls):
        try:
            if cls.client.is_connected():
                cls.client.disconnect()
            cls.client.connect(DNSEConsts.BROKER, DNSEConsts.PORT, keepalive=120)
            return cls.client
        except Exception as e:
            LOGGER.error(f"Connection error: {e}")
            return None

    @classmethod
    def on_connect(cls, client, userdata, flags, rc, properties=None):
        if rc == 0 and client.is_connected():
            LOGGER.info("Connected to MQTT Broker!")
            cls.client.subscribe(MQTT_TOPICS)
            LOGGER.info(f"Subscribed to {[t[0] for t in MQTT_TOPICS]}")
        else:
            LOGGER.error(f"Failed to connect, return code {rc}")

    @classmethod
    def on_disconnect(cls, client, userdata, rc, properties=None):
        LOGGER.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, DNSEConsts.FIRST_RECONNECT_DELAY
        while reconnect_count < DNSEConsts.MAX_RECONNECT_COUNT:
            LOGGER.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                LOGGER.info("Reconnected successfully!")
                return
            except Exception as err:
                LOGGER.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= DNSEConsts.RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, DNSEConsts.MAX_RECONNECT_DELAY)
            reconnect_count += 1
        LOGGER.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
        cls.FLAG_EXIT = True

    @classmethod
    def clean_up(cls):
        if cls.client.is_connected():
            cls.client.unsubscribe(cls.topic)
            cls.client.disconnect()
            LOGGER.info(
                f"Unsubscribed from {cls.topic} and disconnected from MQTT Broker!"
            )

    @classmethod
    def on_message(cls, client, userdata, msg):
        try:
            # Chỉ đưa vào queue, không xử lý nặng ở đây
            MESSAGE_QUEUE.put((msg.topic, msg.payload.decode('utf-8')))
            # LOGGER.info(f"Received message on topic '{msg.topic} - {msg.payload.decode('utf-8')}'.")
            LOGGER.info(f"Received message on topic '{msg.topic}'.")
        except Exception as e:
            LOGGER.error(f"Lỗi trong on_message khi đưa vào queue: {e}", exc_info=True)