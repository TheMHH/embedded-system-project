.PHONY: help broker-up broker-down broker-restart broker-logs broker-status install run test

DOCKER_COMPOSE = docker-compose
VENV_DIR = .venv
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
PYTHON_SCRIPT = $(VENV_DIR)/bin/python
SCRIPT = python-server/face_tracker_server.py
TEST_SCRIPT = python-server/test_mqtt.py

help:
	@echo "Face Tracker Project Makefile"
	@echo ""
	@echo "Infrastructure targets:"
	@echo "  broker-up       - Start the MQTT broker (docker-compose up -d)"
	@echo "  broker-down     - Stop the MQTT broker (docker-compose down)"
	@echo "  broker-restart  - Restart the MQTT broker"
	@echo "  broker-logs     - View MQTT broker logs"
	@echo "  broker-status   - Check MQTT broker status"
	@echo ""
	@echo "Python server targets:"
	@echo "  install         - Setup virtual environment and install dependencies"
	@echo "  run             - Run the face tracker server"
	@echo "  test            - Test MQTT broker connection"

broker-up:
	@echo "Starting MQTT broker..."
	$(DOCKER_COMPOSE) up -d
	@echo "MQTT broker started. Use 'make broker-logs' to view logs."

broker-down:
	@echo "Stopping MQTT broker..."
	$(DOCKER_COMPOSE) down
	@echo "MQTT broker stopped."

broker-restart: broker-down broker-up
	@echo "MQTT broker restarted."

broker-logs:
	@echo "Showing MQTT broker logs (Ctrl+C to exit)..."
	$(DOCKER_COMPOSE) logs -f mosquitto

broker-status:
	@echo "MQTT broker status:"
	$(DOCKER_COMPOSE) ps

install:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r python-server/requirements.txt
	@echo "Dependencies installed"

run:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@echo "Starting face tracker server..."
	$(PYTHON_SCRIPT) $(SCRIPT)

test:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@echo "Running MQTT broker test..."
	$(PYTHON_SCRIPT) $(TEST_SCRIPT)

