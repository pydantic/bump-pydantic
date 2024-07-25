import importlib
import io
import sys
from contextlib import contextmanager

import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.replace_imports import ReplaceImportsCodemod


def is_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


class TestReplaceImportsCommand(CodemodTest):
    TRANSFORM = ReplaceImportsCodemod

    @contextmanager
    def capture_stdout(self):
        new_stdout = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = new_stdout
        yield new_stdout
        sys.stdout = old_stdout

    def test_base_settings(self) -> None:
        before = """
        from pydantic import BaseSettings
        """
        after = """
        from pydantic_settings import BaseSettings
        """
        self.assertCodemod(before, after)

        with self.capture_stdout() as captured:
            self.assertCodemod(before, after)

        if is_package_installed("pydantic_settings"):
            assert captured.getvalue().strip() == "", "stdout is not empty as expected."
        else:
            expected_stdout = "#todo: please install pydantic_settings"
            assert captured.getvalue().strip() == expected_stdout

    def test_noop_base_settings(self) -> None:
        code = """
        from potato import BaseSettings
        """
        with self.capture_stdout() as captured:
            self.assertCodemod(code, code)
        assert captured.getvalue().strip() == "", "stdout is not empty as expected."

    @pytest.mark.xfail(reason="To be implemented.")
    def test_base_settings_as(self) -> None:
        before = """
        from pydantic import BaseSettings as Potato
        """
        after = """
        from pydantic_settings import BaseSettings as Potato
        """
        self.assertCodemod(before, after)

    def test_color(self) -> None:
        before = """
        from pydantic import Color
        """
        after = """
        from pydantic_extra_types.color import Color
        """

        with self.capture_stdout() as captured:
            self.assertCodemod(before, after)

        if is_package_installed("pydantic_extra_types"):
            assert captured.getvalue().strip() == "", "stdout is not empty as expected."
        else:
            expected_stdout = "#todo: please install pydantic_extra_types"
            assert captured.getvalue().strip() == expected_stdout

    def test_color_full(self) -> None:
        before = """
        from pydantic.color import Color
        """
        after = """
        from pydantic_extra_types.color import Color
        """
        with self.capture_stdout() as captured:
            self.assertCodemod(before, after)

        if is_package_installed("pydantic_extra_types"):
            assert captured.getvalue().strip() == "", "stdout is not empty as expected."
        else:
            expected_stdout = "#todo: please install pydantic_extra_types"
            assert captured.getvalue().strip() == expected_stdout

    def test_noop_color(self) -> None:
        code = """
        from potato import Color
        """
        self.assertCodemod(code, code)
        with self.capture_stdout() as captured:
            self.assertCodemod(code, code)
        assert captured.getvalue().strip() == "", "stdout is not empty as expected."

    def test_payment_card_number(self) -> None:
        before = """
        from pydantic import PaymentCardNumber
        """
        after = """
        from pydantic_extra_types.payment import PaymentCardNumber
        """
        with self.capture_stdout() as captured:
            self.assertCodemod(before, after)

        if is_package_installed("pydantic_extra_types"):
            assert captured.getvalue().strip() == "", "stdout is not empty as expected."
        else:
            expected_stdout = "#todo: please install pydantic_extra_types"
            assert captured.getvalue().strip() == expected_stdout

    def test_payment_card_brand(self) -> None:
        before = """
        from pydantic.payment import PaymentCardBrand
        """
        after = """
        from pydantic_extra_types.payment import PaymentCardBrand
        """
        with self.capture_stdout() as captured:
            self.assertCodemod(before, after)

        if is_package_installed("pydantic_extra_types"):
            assert captured.getvalue().strip() == "", "stdout is not empty as expected."
        else:
            expected_stdout = "#todo: please install pydantic_extra_types"
            assert captured.getvalue().strip() == expected_stdout

    def test_noop_payment_card_number(self) -> None:
        code = """
        from potato import PaymentCardNumber
        """
        with self.capture_stdout() as captured:
            self.assertCodemod(code, code)
        assert captured.getvalue().strip() == "", "stdout is not empty as expected."

    def test_noop_payment_card_brand(self) -> None:
        code = """
        from potato import PaymentCardBrand
        """
        with self.capture_stdout() as captured:
            self.assertCodemod(code, code)
        assert captured.getvalue().strip() == "", "stdout is not empty as expected."

    def test_both_payment(self) -> None:
        before = """
        from pydantic.payment import PaymentCardNumber, PaymentCardBrand
        """
        after = """
        from pydantic_extra_types.payment import PaymentCardBrand, PaymentCardNumber
        """
        with self.capture_stdout() as captured:
            self.assertCodemod(before, after)

        if is_package_installed("pydantic_extra_types"):
            assert captured.getvalue().strip() == "", "stdout is not empty as expected."
        else:
            expected_stdout = "#todo: please install pydantic_extra_types"
            assert captured.getvalue().strip() == expected_stdout
