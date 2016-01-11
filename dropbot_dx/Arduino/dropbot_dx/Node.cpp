#include "Node.h"

namespace dropbot_dx {

void Node::begin() {
  config_.set_buffer(get_buffer());
  config_.validator_.set_node(*this);
  config_.reset();
  config_.load();
  pinMode(LIGHT_PIN, OUTPUT);
  servo_.attach(SERVO_PIN);
  state_.set_buffer(get_buffer());
  state_.validator_.set_node(*this);
  state_.reset();
  // Mark light enabled and magnet engaged state for validation.
  state_._.has_light_enabled = true;
  state_._.has_magnet_engaged = true;
  // Validate state to trigger on-changed handling for state fields that are
  // set (which initializes the state to the default values supplied in the
  // state protocol buffer definition).
  state_.validate();
  // Start Serial after loading config to set baud rate.
#if !defined(DISABLE_SERIAL)
  Serial.begin(config_._.baud_rate);
#endif  // #ifndef DISABLE_SERIAL
  // Set i2c clock-rate to 400kHz.
  TWBR = 12;
}


void Node::set_i2c_address(uint8_t value) {
  // Validator expects `uint32_t` by reference.
  uint32_t address = value;
  /* Validate address and update the active `Wire` configuration if the
    * address is valid. */
  config_.validator_.i2c_address_(address, config_._.i2c_address);
  config_._.i2c_address = address;
}

}  // namespace dropbot_dx
