import logging
import markdown
import openai

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from dependencies import get_templates, get_settings
from models.article import Article, Group
from models.database import get_session 
from pydantic import field_validator


from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)

router = APIRouter()

class ArticleCreate(BaseModel):
    title: str
    group_id: int 
    content: str
    key: str

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('标题不能为空')
        if len(v) > 100:
            raise ValueError('标题长度不能超过100个字符')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('文章内容不能为空')
        return v

    class Config:
        error_msg_templates = {
            'type_error.integer': '请输入有效的数字',
            'value_error.missing': '此字段不能为空',
            'type_error.str': '请输入文本内容'
        }

class GroupCreate(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('分组名称不能为空')
        if len(v) > 100:
            raise ValueError('分组名称不能超过100个字符')
        return v

@router.post('/add', status_code=status.HTTP_201_CREATED)
async def add(
    article: ArticleCreate, 
    db: Session = Depends(get_session),
    settings = Depends(get_settings)
):
    logger.info(f"Adding article: {article}")
    
    if article.key != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": status.HTTP_401_UNAUTHORIZED,
                "message": "管理员密钥验证失败，请检查密钥是否正确"
            }
        )
        
    try:
        db_article = Article(
            title=article.title,
            group_id=article.group_id,
            content=article.content,
        )
        db_article.summary = await db_article.generate_summary()
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return {
            "code": status.HTTP_201_CREATED,
            "message": "success",
            "data": db_article
        }
    except ValidationError as e:
        error_msgs = [f"{err['msg']}" for err in e.errors()]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "，".join(error_msgs)
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding article: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": str(e)
            }
        )
@router.post('/update')
def update(title: str, group_id: int, content: str, article_id: int, db = Depends(get_session)):
    article = db.query(Article).filter(Article.id == article_id).first()
    article.title = title
    article.group_id = group_id
    article.content = content
    db.commit()
    db.refresh(article)
    return article

@router.post('/list')
def list(group_name: str = None, db = Depends(get_session)):
    if group_name:
        group = db.query(Group).filter(Group.name == group_name).first()
        if group:
            articles = db.query(Article).filter(Article.group_id == group.id).all()
        else:
            articles = []
    else:
        articles = db.query(Article).all()
    for article in articles:
        article.content = markdown.markdown(article.content)
    return articles

@router.get('/blog', response_class=HTMLResponse)
def blog(
    request: Request, 
    templates: Jinja2Templates = Depends(get_templates),
    db = Depends(get_session)
):
    groups = db.query(Group).all()
    selected_group_id = request.query_params.get('group_id')
    if not selected_group_id:
        selected_group_id = 1
    if selected_group_id:
        articles = db.query(Article).filter(Article.group_id == selected_group_id).all()
    else:
        articles = []
        
    for article in articles:
        article.content = markdown.markdown(article.content)

    return templates.TemplateResponse("blog.html", {
        "request": request,
        "groups": groups,
        "articles": articles
    })

@router.get('/add_vanshin', response_class=HTMLResponse)
async def add_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    db = Depends(get_session),
):
    groups = db.query(Group).all()
    return templates.TemplateResponse("add_article.html", {
        "request": request,
        "groups": groups
    })

@router.post('/add_group')
async def add_group(
    group: GroupCreate,
    db: Session = Depends(get_session)
):
    try:
        existing_group = db.query(Group).filter(Group.name == group.name).first()
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "该分组名称已存在"
                }
            )

        new_group = Group(name=group.name)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)

        return {
            "code": status.HTTP_201_CREATED,
            "message": "success",
            "id": new_group.id,
            "name": new_group.name
        }

    except ValidationError as e:
        error_msgs = [f"{err['msg']}" for err in e.errors()]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "，".join(error_msgs)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding group: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "服务器错误"
            }
        )

@router.get('/')
def root(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    db = Depends(get_session)
):
    return blog(request, templates, db)
