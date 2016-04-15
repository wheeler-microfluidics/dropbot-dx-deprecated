import time

from path_helpers import path


try:
    from base_node_rpc.proxy import ConfigMixinBase, StateMixinBase
    from .node import (Proxy as _Proxy, I2cProxy as _I2cProxy,
                       SerialProxy as _SerialProxy)
    from .config import Config
    from .state import State


    class ConfigMixin(ConfigMixinBase):
        @property
        def config_class(self):
            return Config


    class StateMixin(StateMixinBase):
        @property
        def state_class(self):
            return State


    class ProxyMixin(ConfigMixin, StateMixin):
        '''
        Mixin class to add share common functionality between `Proxy`,
        `SerialProxy`, etc. classes.
        '''
        host_package_name = str(path(__file__).parent.name.replace('_', '-'))

        def __del__(self):
            try:
                self.update_state(light_enabled=False, magnet_engaged=False)
            except IOError:
                pass
            super(ProxyMixin, self).__del__()

        def get_environment_state(self, i2c_address=0x27):
            '''
            Acquire temperature and humidity from Honeywell HIH6000 series
            sensor.

            [1]: http://sensing.honeywell.com/index.php/ci_id/142171/la_id/1/document/1/re_id/0
            '''
            import pandas as pd

            # Trigger measurement.
            self.i2c_write(i2c_address, [])
            time.sleep(.01)

            while True:
                # Read 4 bytes from sensor.
                humidity_data, temperature_data = self.i2c_read(i2c_address,
                                                                4).view('>u2')
                status_code = (humidity_data >> 14) & 0x03
                if status_code == 0:
                    # Measurement completed successfully.
                    break
                elif status_code > 1:
                    raise IOError('Error reading from sensor.')
                # Measurement data is stale (i.e., measurement still in
                # progress).  Try again.
                time.sleep(.001)

            # See URL from docstring for source of equations.
            relative_humidity = float(humidity_data & 0x03FFF) / ((1 << 14) - 2)
            temperature_celcius = (float((temperature_data >> 2) & 0x3FFF) /
                                   ((1 << 14) - 2) * 165 - 40)

            return pd.Series([relative_humidity, temperature_celcius],
                             index=['relative_humidity',
                                    'temperature_celcius'])

    class Proxy(ProxyMixin, _Proxy):
        pass

    class I2cProxy(ProxyMixin, _I2cProxy):
        pass

    class SerialProxy(ProxyMixin, _SerialProxy):
        pass
except (ImportError, TypeError):
    Proxy = None
    I2cProxy = None
    SerialProxy = None
