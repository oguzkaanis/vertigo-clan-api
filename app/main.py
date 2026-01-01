from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .database import SessionLocal, engine
from .models import Clan
from pydantic import BaseModel

app = FastAPI(title="Clan API")

# Health check
@app.get("/")
def health_check():
    return {"status": "ok"}

# Pydantic schema
class ClanCreate(BaseModel):
    name: str
    description: str = None  # optional

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tabloyu oluştur (sadece bir kez, uygulama başında)
Clan.metadata.create_all(bind=engine)

# POST /clans -> DB'ye yaz
@app.post("/clans")
def create_clan(clan: ClanCreate, db: Session = Depends(get_db)):
    new_clan = Clan(
        name=clan.name,
        description=clan.description
    )
    db.add(new_clan)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Clan name already exists")
    db.refresh(new_clan)
    return new_clan

# GET /clans -> DB'den tüm clan'ları al
@app.get("/clans")
def list_clans(db: Session = Depends(get_db)):
    return db.query(Clan).all()

# GET /clans/search?q=xxx -> DB'de arama
@app.get("/clans/search")
def search_clans(q: str, db: Session = Depends(get_db)):
    if len(q) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")
    return db.query(Clan).filter(Clan.name.ilike(f"%{q}%")).all()

from fastapi import Path

@app.delete("/clans/{clan_id}")
def delete_clan(clan_id: int = Path(..., description="The ID of the clan to delete"), db: Session = Depends(get_db)):
    clan = db.query(Clan).filter(Clan.id == clan_id).first()
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")
    db.delete(clan)
    db.commit()
    return {"detail": f"Clan {clan.name} deleted successfully"}
