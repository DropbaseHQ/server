import pandas as pd

from server.controllers.utils import find_functions_by_signature


class A:
    pass
class B:
    pass
class C:
    pass

def f0() -> C:
    return
def f1(x1: A) -> C:
    return
def f2(x1: B) -> C:
    return
def f3(x1: A, x2: B) -> C:
    return
def f4(x1: A, x2: A) -> C:
    return
def f5(x1: A, x2: A, x3: B) -> C:
    return


def test_find_functions_by_signature():
    import sys
    module = sys.modules[__name__]

    assert find_functions_by_signature(
        module,
        req_param_types=[],
        opt_param_types=[],
        return_type=C
    ) == ["f0"]

    assert find_functions_by_signature(
        module,
        req_param_types=[A],
        opt_param_types=[],
        return_type=C
    ) == ["f1"]

    assert find_functions_by_signature(
        module,
        req_param_types=[A, B],
        opt_param_types=[],
        return_type=C
    ) == ["f3"]

    assert find_functions_by_signature(
        module,
        req_param_types=[A],
        opt_param_types=[B],
        return_type=C
    ) == ["f1", "f3"]

    assert find_functions_by_signature(
        module,
        req_param_types=[A, A],
        opt_param_types=[],
        return_type=C
    ) == ["f4"]

    assert find_functions_by_signature(
        module,
        req_param_types=[A, B],
        opt_param_types=[A],
        return_type=C
    ) == ["f3", "f5"]
