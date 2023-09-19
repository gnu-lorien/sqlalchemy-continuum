import sqlalchemy as sa
from sqlalchemy.sql.expression import bindparam

from .utils import version_table, get_versioning_manager


class VersionExpressionReflector(sa.sql.visitors.ReplacingCloningVisitor):
    def __init__(self, parent, relationship):
        self.parent = parent
        self.relationship = relationship

    def replace(self, column):
        if not isinstance(column, sa.Column):
            return
        try:
            table = version_table(column.table, get_versioning_manager(self.parent))
        except KeyError:
            reflected_column = column
        else:
            for c in table.c.values():
                if c.name == column.name:
                    reflected_column = c
                    break
            else:
                raise RuntimeError("Could not find column when reflecting a versioned expression")
            if (
                column in self.relationship.local_columns and
                table == self.parent.__table__
            ):
                reflected_column = bindparam(
                    column.key,
                    getattr(self.parent, column.key)
                )

        return reflected_column

    def __call__(self, expr):
        return self.traverse(expr)
