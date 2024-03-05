from types import ModuleType as __ModuleType
from . import (test_flow_controls,
               test_function,
               test_header,
               test_jmc_function,
               test_jmc_txt,
               test_nbt,
               test_new,
               test_syntax_errors,
               test_variable
               )

ALL: tuple[__ModuleType, ...] = (test_flow_controls,
                                 test_function,
                                 test_header,
                                 test_jmc_function,
                                 test_jmc_txt,
                                 test_nbt,
                                 test_new,
                                 test_syntax_errors,
                                 test_variable
                                 )
