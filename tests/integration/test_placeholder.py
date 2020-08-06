import pytest


class TestPlaceholder:
    """For tox to find tests the following must be true:
        - Names of test files begin with 'test'
        - Names of classes containing tests begin with 'Test'
        - Names of functions to be run as tests begin with 'Test'
        """

    def test_trivial(self):

        x = 1
        y = 1

        assert x == y

    @pytest.mark.parametrize("value", ["atgcX", "L:", "3", "AUGC~", ":gagagag"])
    def test_trivial_with_parameters(self, value):

        with pytest.raises(AssertionError):
            assert value == 1
