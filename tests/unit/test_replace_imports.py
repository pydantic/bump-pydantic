import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.replace_imports import ReplaceImportsCodemod


class TestReplaceImportsCommand(CodemodTest):
    TRANSFORM = ReplaceImportsCodemod

    def test_base_settings(self) -> None:
        before = """
        from pydantic import BaseSettings
        """
        after = """
        from pydantic_settings import BaseSettings
        """
        self.assertCodemod(before, after)

    def test_noop_base_settings(self) -> None:
        code = """
        from potato import BaseSettings
        """
        self.assertCodemod(code, code)

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
        self.assertCodemod(before, after)

    def test_color_full(self) -> None:
        before = """
        from pydantic.color import Color
        """
        after = """
        from pydantic_extra_types.color import Color
        """
        self.assertCodemod(before, after)

    def test_noop_color(self) -> None:
        code = """
        from potato import Color
        """
        self.assertCodemod(code, code)

    def test_payment_card_number(self) -> None:
        before = """
        from pydantic import PaymentCardNumber
        """
        after = """
        from pydantic_extra_types.payment import PaymentCardNumber
        """
        self.assertCodemod(before, after)

    def test_payment_card_brand(self) -> None:
        before = """
        from pydantic.payment import PaymentCardBrand
        """
        after = """
        from pydantic_extra_types.payment import PaymentCardBrand
        """
        self.assertCodemod(before, after)

    def test_noop_payment_card_number(self) -> None:
        code = """
        from potato import PaymentCardNumber
        """
        self.assertCodemod(code, code)

    def test_noop_payment_card_brand(self) -> None:
        code = """
        from potato import PaymentCardBrand
        """
        self.assertCodemod(code, code)

    def test_both_payment(self) -> None:
        before = """
        from pydantic.payment import PaymentCardNumber, PaymentCardBrand
        """
        after = """
        from pydantic_extra_types.payment import PaymentCardBrand, PaymentCardNumber
        """
        self.assertCodemod(before, after)
