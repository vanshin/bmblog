from models import Base
from services.ai_service import generate_article_summary
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column


class Article(Base):

    __tablename__ = "article"
    __table_args__ = (
        {'comment': '文章'},
    )

    title: Mapped[str] = mapped_column(String(200), comment='标题')
    group_id: Mapped[int] = mapped_column(Integer, comment='分组ID')
    content: Mapped[str] = mapped_column(Text, comment='markdown内容')
    summary: Mapped[str] = mapped_column(Text, comment='文章摘要')

    async def generate_summary(self) -> str:
        self.summary = await generate_article_summary(self.content)
        return self.summary


class Group(Base):
    __tablename__ = "group"
    __table_args__ = (
        {'comment': '文章分组'},
    )

    name: Mapped[str] = mapped_column(String(200), comment='分组名称')
