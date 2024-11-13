from models import Base
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column


class Article(Base):

    __tablename__ = "article"
    __table_args__ = (
        {'comment': 'pdf转换以后的markdown'},
    )

    title: Mapped[int] = mapped_column(String(200), comment='')
    group_id: Mapped[int] = mapped_column(Integer, comment='group ID')
    content: Mapped[str] = mapped_column(Text, comment='markdown内容')


class Group(Base):
    __tablename__ = "group"
    __table_args__ = (
        {'comment': '文章分组'},
    )

    content: Mapped[str] = mapped_column(Text)
