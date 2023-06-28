from libcst import matchers as m
from typing import List

import libcst as cst
from libcst import matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand
from libcst.codemod.visitors import AddImportsVisitor
from libcst.codemod import VisitorBasedCodemodCommand

IMPORT_VALIDATOR = m.Module(
    body=[
        m.ZeroOrMore(),
        m.SimpleStatementLine(
            body=[
                m.ZeroOrMore(),
                m.ImportFrom(
                    module=m.Name("pydantic"),
                    names=[
                        m.ZeroOrMore(),
                        m.ImportAlias(name=m.Name("validator")),
                        m.ZeroOrMore(),
                    ],
                ),
                m.ZeroOrMore(),
            ],
        ),
        m.ZeroOrMore(),
    ]
)


class ValidatorCodemod(VisitorBasedCodemodCommand):
    ...
