from fastapi import APIRouter, Depends, Request
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from dependencies import get_templates
from models.article import Article, Group
from models.database import get_session 


router = APIRouter()
from fastapi import HTTPException, status
from pydantic import BaseModel
import markdown

class ArticleCreate(BaseModel):
    title: str
    group_id: int 
    content: str

@router.post('/add', status_code=status.HTTP_201_CREATED)
def add(article: ArticleCreate, db: Session = Depends(get_session)):
    try:
        db_article = Article(
            title=article.title,
            group_id=article.group_id,
            content=article.content
        )
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
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

@router.get('/add', response_class=HTMLResponse)
def add_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    db = Depends(get_session)
):
    groups = db.query(Group).all()
    return templates.TemplateResponse("add_article.html", {
        "request": request,
        "groups": groups
    })

