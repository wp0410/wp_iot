# wp_iot

Object classes for building Raspberry PI based IOT systems.

## iot_base

1. Base classes (e.g. base class for hardware, sensor and actor controllers);
1. IOT message classes (input probe, health status, etc.)

## iot_repository

Classes for storing IOT configuration settings in a SQLite repository (implemented
in wp_repository).

## iot_configuation

Facade class to access the configuration settings in the SQLite repository in a
structured and convenient way.

## iot_hardware

Classes implementing the interaction with hardware components connected to the 
Raspberry PI. Currently, the following components are supported:
1. ADS1115 (analog to digital input converter connected to the I2C bus)

"handler" classes controlling the hardware components by initiating probing of the hardware
components and publishing the results to a MQTT broker, or by receiving messages
from a MQTT broker and initiating an action on the controlled hardware device.

## iot_recorder

"handler" instances subscribing to topics on a MQTT broker and storing the received
messages in a SQLite repository.

## iot_runtime

Classes representing the process (iot_host) and control threads (iot_agent) during
runtime.

## iot_sensor

In progress.

## iot_actor

Coming soon.