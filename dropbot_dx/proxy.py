from path_helpers import path
from arduino_rpc.protobuf import resolve_field_values


try:
    from .node import (Proxy as _Proxy, I2cProxy as _I2cProxy,
                       SerialProxy as _SerialProxy)

    class ProxyMixin(object):
        '''
        Mixin class to add convenience wrappers around methods of the generated
        `node.Proxy` class.

        For example, expose config and state getters/setters as attributes.
        '''
        host_package_name = str(path(__file__).parent.name.replace('_', '-'))

        @property
        def _config_pb(self):
            from .config import Config

            return Config.FromString(self.serialize_config().tostring())
        
        @property
        def config(self):
            return (resolve_field_values(self._config_pb, set_default=True)
                    ).set_index(['full_name'])['value']

        @config.setter
        def config(self, value):
            # convert pandas Series to a dictionary if necessary
            if hasattr(value, 'to_dict'):
                value = value.to_dict()

            self.update_config(**value)
        
        @property
        def _state_pb(self):
            from .config import State

            return State.FromString(self.serialize_state().tostring())

        @property
        def state(self):
            return (resolve_field_values(self._state_pb, set_default=True)
                    ).set_index(['full_name'])['value']

        @state.setter
        def state(self, value):
            # convert pandas Series to a dictionary if necessary
            if hasattr(value, 'to_dict'):
                value = value.to_dict()
                
            self.update_state(**value)


        def update_config(self, **kwargs):
            '''
            Update fields in the config object based on keyword arguments.

            By default, these values will be saved to EEPROM. To prevent this
            (e.g., to verify system behavior before committing the changes),
            you can pass the special keyword argument 'save=False'. In this case,
            you will need to call the method save_config() to make your changes
            persistent.
            '''
 
            from .config import Config

            save = True
            if 'save' in kwargs.keys() and not kwargs.pop('save'):
                save = False

            # convert dictionary to a protobuf
            config_pb = Config(**kwargs)
                
            return_code = super(ProxyMixin, self).update_config(config_pb)

            if save:
                super(ProxyMixin, self).save_config()

            return return_code

        def update_state(self, **kwargs):
            from .config import State

            state = State(**kwargs)
            return super(ProxyMixin, self).update_state(state)

        def __del__(self):
            self.update_state(light_enabled=False, magnet_engaged=False)
            super(ProxyMixin, self).__del__()


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
