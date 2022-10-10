from types import ModuleType as __ModuleType
from . import (test_flow_controls,
               test_function,
               test_jmc_function,
               test_new,
               test_variable,
               test_header
               )

ALL: tuple[__ModuleType, ...] = (test_flow_controls,
                                 test_function,
                                 test_jmc_function,
                                 test_new,
                                 test_variable,
                                 test_header
                                 )
