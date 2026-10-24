from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


def _get_owned_product(db, product_id: int, user_id: int) -> Product:
    """Ownership is enforced in the query itself. Not-yours and missing both give 404."""
    product = db.scalar(select(Product).where(Product.id == product_id, Product.user_id == user_id))
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, current_user: CurrentUser, db: DbSession):
    product = Product(user_id=current_user.id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("", response_model=list[ProductRead])
def list_products(
    current_user: CurrentUser,
    db: DbSession,
    category: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    stmt = select(Product).where(Product.user_id == current_user.id)
    if category:
        stmt = stmt.where(Product.category == category)
    stmt = stmt.order_by(Product.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, current_user: CurrentUser, db: DbSession):
    return _get_owned_product(db, product_id, current_user.id)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, current_user: CurrentUser, db: DbSession):
    product = _get_owned_product(db, product_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, current_user: CurrentUser, db: DbSession):
    product = _get_owned_product(db, product_id, current_user.id)
    db.delete(product)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
