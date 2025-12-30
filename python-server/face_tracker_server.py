#!/usr/bin/env python3
"""
Image Position Tracker Server
Receives images from camera/image MQTT topic, extracts position, and publishes
servo position commands to servo/position topic.
"""

import paho.mqtt.client as mqtt
import logging
import cv2
import numpy as np
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = "position_tracker_server"
IMAGE_TOPIC = "camera/image"
POSITION_TOPIC = "servo/position"

MIN_POSITION = 0
MAX_POSITION = 180

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def extract_position(image_data: bytes) -> Optional[int]:
    """
    Extract position from image data by detecting face and mapping x position to 0-180.
    
    Args:
        image_data: JPEG image bytes
        
    Returns:
        Position value (0-180) or None if no face detected
    """
    try:
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.warning("Failed to decode image")
            return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            logger.debug("No face detected")
            return None
        
        x, y, w, h = faces[0]
        
        face_center_x = x + (w / 2)
        
        image_width = img.shape[1]
        
        position = int(np.interp(face_center_x, [0, image_width], [0, 180]))
        
        logger.debug(f"Face center x: {face_center_x:.1f}, Image width: {image_width}, Position: {position}")
        
        return position
        
    except Exception as e:
        logger.error(f"Error in extract_position: {e}", exc_info=True)
        return None


def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects to broker."""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        client.subscribe(IMAGE_TOPIC)
        logger.info(f"Subscribed to topic: {IMAGE_TOPIC}")
    else:
        logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")


def on_message(client, userdata, msg):
    """Callback when a message is received on subscribed topic."""
    try:
        image_data = msg.payload
        logger.debug(f"Received image: {len(image_data)} bytes")
        
        position = extract_position(image_data)
        
        if position is None:
            logger.debug("Position extraction returned None, skipping")
            return
        
        position = max(MIN_POSITION, min(MAX_POSITION, position))
        position_str = str(position)
        
        result = client.publish(POSITION_TOPIC, position_str)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Published servo position: {position}")
        else:
            logger.error(f"Failed to publish servo position. Return code: {result.rc}")
            
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)


def initialize_client() -> mqtt.Client:
    """Initialize and configure MQTT client."""
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    return client


def main():
    """Main function to run the position tracker server."""
    logger.info("Starting Position Tracker Server...")
    
    client = initialize_client()
    
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        logger.info(f"Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        return
    
    try:
        logger.info("Position Tracker Server running. Press Ctrl+C to stop.")
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Position Tracker Server...")
        client.disconnect()
        logger.info("Server stopped.")


if __name__ == "__main__":
    main()

