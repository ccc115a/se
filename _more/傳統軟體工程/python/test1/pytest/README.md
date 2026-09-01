# pytest

```
(base) $ pytest
====================== test session starts ======================
platform darwin -- Python 3.8.5, pytest-7.1.3, pluggy-0.13.1
rootdir: /Users/csienqu/Desktop/ccc/alg/A6-python/test1/pytest
collected 2 items                                               

test_sum.py .F                                            [100%]

=========================== FAILURES ============================
________________________ test_sum_tuple _________________________

    def test_sum_tuple():
>       assert sum((1, 2, 2)) == 6, "Should be 6"
E       AssertionError: Should be 6
E       assert 5 == 6
E        +  where 5 = sum((1, 2, 2))

test_sum.py:5: AssertionError
==================== short test summary info ====================
FAILED test_sum.py::test_sum_tuple - AssertionError: Should be 6
================== 1 failed, 1 passed in 0.11s ==================
```
