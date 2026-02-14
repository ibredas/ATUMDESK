import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_, and_
from pydantic import BaseModel

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.kb_article import KBArticle
from app.models.kb_category import KBCategory

router = APIRouter()

# --- Pydantic Models ---

class ArticleCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[uuid.UUID] = None
    is_internal: bool = False
    is_published: bool = False

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    is_internal: Optional[bool] = None
    is_published: Optional[bool] = None

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    is_internal: bool = False

class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    is_internal: bool
    parent_id: Optional[uuid.UUID]

class ArticleResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    excerpt: Optional[str]
    content: Optional[str] # Full content detailed view only? Let's include for now
    is_internal: bool
    is_published: bool
    view_count: int
    helpful_count: int
    category_id: Optional[uuid.UUID]
    updated_at: datetime

# --- Routes: Categories ---

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List categories. Customers see public only."""
    query = select(KBCategory).where(KBCategory.organization_id == current_user.organization_id)
    
    if current_user.role == UserRole.CUSTOMER_USER:
        query = query.where(KBCategory.is_internal == False)
        
    result = await db.execute(query.order_by(KBCategory.display_order, KBCategory.name))
    return result.scalars().all()

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create category (Agent/Admin only)"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    cat = KBCategory(
        organization_id=current_user.organization_id,
        name=data.name,
        description=data.description,
        parent_id=data.parent_id,
        is_internal=data.is_internal
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat

# --- Routes: Articles ---

@router.get("/articles", response_model=List[ArticleResponse])
async def list_articles(
    search: Optional[str] = None,
    category_id: Optional[uuid.UUID] = None,
    visibility: str = Query("public", regex="^(public|internal|all)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    List articles with visibility filters.
    Customer: Forced 'public' only.
    Agent: Can see 'internal' or 'all'.
    """
    
    # Enforce Tenant
    query = select(KBArticle).where(KBArticle.organization_id == current_user.organization_id)
    
    # 1. Visibility Filter
    if current_user.role == UserRole.CUSTOMER_USER:
        # Customers NEVER see internal or unpublished
        query = query.where(
            KBArticle.is_internal == False,
            KBArticle.is_published == True
        )
    else:
        # Agents
        if visibility == "public":
             query = query.where(KBArticle.is_internal == False)
        elif visibility == "internal":
             query = query.where(KBArticle.is_internal == True)
        # 'all' shows everything
        
    # 2. Category Filter
    if category_id:
        query = query.where(KBArticle.category_id == category_id)
        
    # 3. Search (Simple ILIKE for MVP, Full Text Vector later)
    if search:
        term = f"%{search}%"
        query = query.where(or_(
            KBArticle.title.ilike(term),
            KBArticle.content.ilike(term)
        ))
        
    result = await db.execute(query.order_by(desc(KBArticle.updated_at)))
    items = result.scalars().all()
    
    # Map to response (Pydantic can do this mostly automatically but explicit is safer for audit)
    return [
        ArticleResponse(
            id=a.id,
            title=a.title,
            slug=a.slug,
            excerpt=a.excerpt,
            content=a.content, # In list view maybe truncate? keeping full for simplicity
            is_internal=a.is_internal,
            is_published=a.is_published,
            view_count=a.view_count,
            helpful_count=a.helpful_count,
            category_id=a.category_id,
            updated_at=a.updated_at
        ) for a in items
    ]

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get single article. Increments view count."""
    query = select(KBArticle).where(
        KBArticle.id == article_id,
        KBArticle.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    # Visibility Check
    if current_user.role == UserRole.CUSTOMER_USER:
        if article.is_internal or not article.is_published:
             raise HTTPException(status_code=404, detail="Article not found")
             
    # Increment View Count (Fire and forget, or await)
    article.view_count += 1
    await db.commit() # Commit the view count
    
    return ArticleResponse(
            id=article.id,
            title=article.title,
            slug=article.slug,
            excerpt=article.excerpt,
            content=article.content,
            is_internal=article.is_internal,
            is_published=article.is_published,
            view_count=article.view_count,
            helpful_count=article.helpful_count,
            category_id=article.category_id,
            updated_at=article.updated_at
    )

@router.post("/articles", response_model=ArticleResponse)
async def create_article(
    data: ArticleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create Article (Agent/Admin)"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Generate slug from title (naish implementation)
    base_slug = data.title.lower().replace(" ", "-") # simplistic
    # Check slug uniqueness? For MVP rely on unique constraint error or append uuid
    slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
    
    article = KBArticle(
        organization_id=current_user.organization_id,
        title=data.title,
        slug=slug,
        content=data.content,
        category_id=data.category_id,
        is_internal=data.is_internal,
        is_published=data.is_published,
        created_by=current_user.id,
        published_at=datetime.utcnow() if data.is_published else None
    )
    
    db.add(article)
    await db.commit()
    await db.refresh(article)
    
    return ArticleResponse(
            id=article.id, title=article.title, slug=article.slug, excerpt=article.excerpt,
            content=article.content, is_internal=article.is_internal, is_published=article.is_published,
            view_count=article.view_count, helpful_count=article.helpful_count,
            category_id=article.category_id, updated_at=article.updated_at
    )

@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: uuid.UUID,
    data: ArticleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update Article (Agent/Admin)"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(KBArticle).where(
        KBArticle.id == article_id,
        KBArticle.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    if data.title is not None: article.title = data.title
    if data.content is not None: article.content = data.content
    if data.category_id is not None: article.category_id = data.category_id
    if data.is_internal is not None: article.is_internal = data.is_internal
    if data.is_published is not None: 
        article.is_published = data.is_published
        if data.is_published and not article.published_at:
            article.published_at = datetime.utcnow()
            
    await db.commit()
    await db.refresh(article)
    
    return ArticleResponse(
            id=article.id, title=article.title, slug=article.slug, excerpt=article.excerpt,
            content=article.content, is_internal=article.is_internal, is_published=article.is_published,
            view_count=article.view_count, helpful_count=article.helpful_count,
            category_id=article.category_id, updated_at=article.updated_at
    )

@router.post("/articles/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(
    article_id: uuid.UUID,
    publish: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Publish/Unpublish Article"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(KBArticle).where(
        KBArticle.id == article_id,
        KBArticle.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    article.is_published = publish
    if publish and not article.published_at:
        article.published_at = datetime.utcnow()
        
    await db.commit()
    await db.refresh(article)
    
    return ArticleResponse(
            id=article.id, title=article.title, slug=article.slug, excerpt=article.excerpt,
            content=article.content, is_internal=article.is_internal, is_published=article.is_published,
            view_count=article.view_count, helpful_count=article.helpful_count,
            category_id=article.category_id, updated_at=article.updated_at
    )
