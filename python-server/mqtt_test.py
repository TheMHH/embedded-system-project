"""
MQTT Broker Test Script
Tests the MQTT broker by publishing and receiving messages on a test topic.
"""

import json
import paho.mqtt.client as mqtt
import time
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID_PUB = "test_publisher"
MQTT_CLIENT_ID_SUB = "test_subscriber"
TEST_TOPIC = "test/topic"

test_messages = [
    {"message": "Hello MQTT!", "number": 1, "timestamp": None},
    {"message": "Test message 2", "number": 2, "timestamp": None},
    {"message": "Final test", "number": 3, "timestamp": None},
]

received_messages = []

def run_subscriber():
    logger.info("\nSetting up subscriber...")
    
    def on_connect_sub(client, userdata, flags, rc):
        """Callback when subscriber connects to broker."""
        if rc == 0:
            logger.info("Subscriber connected successfully")
            client.subscribe(TEST_TOPIC)
            logger.info(f"Subscribed to topic: {TEST_TOPIC}")
        else:
            logger.error(f"Subscriber failed to connect, return code {rc}")
    
    def on_message_sub(client, userdata, msg):
        """Callback when subscriber receives a message."""
        payload = json.loads(msg.payload.decode('utf-8'))
        received_messages.append(payload)
        logger.info(f"Received message: {payload}")
    
    subscriber = mqtt.Client(client_id=MQTT_CLIENT_ID_SUB)
    subscriber.on_connect = on_connect_sub
    subscriber.on_message = on_message_sub

    subscriber.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    subscriber.loop_start()
    
    # Wait a moment for the connection and subscription to be established
    time.sleep(0.5)
    
    return subscriber

def run_publisher():
    logger.info("\nSetting up publisher...")

    publisher = mqtt.Client(client_id=MQTT_CLIENT_ID_PUB)
    
    publisher.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    logger.info("Publisher connected successfully")

    logger.info("\nPublishing test messages...")

    for i, msg_data in enumerate(test_messages, 1):
        msg_data["timestamp"] = time.time()
        payload = json.dumps(msg_data)
        
        result = publisher.publish(TEST_TOPIC, payload, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"  Published message {i}: {msg_data['message']}")
        else:
            logger.error(f"  Failed to publish message {i}")
        
        time.sleep(0.5)
    
    return publisher

def test_mqtt_broker():
    """Test MQTT broker by publishing and receiving messages."""
    logger.info("=" * 60)
    logger.info("Starting MQTT Broker Test")
    logger.info("=" * 60)
    
    subscriber = run_subscriber()
    
    publisher = run_publisher()
    
    logger.info("\nWaiting for messages to be received...")
    time.sleep(3)
    
    subscriber.loop_stop()
    subscriber.disconnect()
    
    publisher.disconnect()
    
    logger.info("Test Results")
    logger.info(f"Published messages: {len(test_messages)}")
    logger.info(f"Received messages: {len(received_messages)}")
    
    if len(received_messages) == len(test_messages):
        logger.info("\nSUCCESS: All messages were received!")
    else:
        logger.warning(f"\nWARNING: Only received {len(received_messages)} out of {len(test_messages)} messages")

    return len(received_messages) == len(test_messages)

if __name__ == "__main__":
    try:
        success = test_mqtt_broker()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nTest failed with error: {e}", exc_info=True)
        sys.exit(1)

