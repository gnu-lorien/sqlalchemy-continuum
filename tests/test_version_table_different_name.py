from pytest import mark
import sqlalchemy as sa
from sqlalchemy_continuum import version_class
from sqlalchemy.orm import relationship

from tests import TestCase, create_test_cases


class VersionTableDifferentNameBaseTestCase(TestCase):
    @property
    def options(self):
        base_options = super().options
        base_options["table_name"] = "%s_something_completely_different"
        return base_options

    def create_models(self):
        class TextItem(self.Model):
            __tablename__ = 'text_item'
            __versioned__ = {}

            id = sa.Column(
                '_id', sa.Integer, autoincrement=True, primary_key=True
            )

            name = sa.Column('_name', sa.Unicode(255))
            relationship_with_text_items = relationship("RelationshipWithTextItem", back_populates="text_item")

        self.TextItem = TextItem

        class RelationshipWithTextItem(self.Model):
            __tablename__ = 'relationship_with_text_item'
            __versioned__ = {}

            id = sa.Column('id', sa.Integer, autoincrement=True, primary_key=True)

            text_item_id = sa.Column(sa.Integer, sa.ForeignKey(TextItem.id), nullable=False)
            text_item = relationship('TextItem', back_populates='relationship_with_text_items')

        self.RelationshipWithTextItem = RelationshipWithTextItem


class VersionTableDifferentNameTestCase(VersionTableDifferentNameBaseTestCase):
    def test_insert_relationship(self):
        item = self.TextItem(name=u'Something')
        self.session.add(item)
        self.session.commit()
        related = self.RelationshipWithTextItem(text_item=item)
        self.session.add(related)
        self.session.commit()
        assert related.versions[0].text_item.id == item.id


create_test_cases(VersionTableDifferentNameTestCase)
