from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from fastapi import Depends
from src.utils.db import get_db
from pytz import UTC
from src.assets.model import AssetModel
from src.assets.dtos import AssetEntity
from src.utils.db import SessionLocal
from datetime import datetime, date

def update_lifecycle():
    db = SessionLocal()
    try:
        assets = db.query(AssetModel).filter(AssetModel.meta != {}).all() 
        for asset in assets:
            if asset.meta.get("expires"):
                exp_date = datetime.strptime(asset.meta.get("expires"), "%Y-%m-%d").date()
                if exp_date < date.today():
                    asset.meta["lifecycle_status"] = "expired"
        db.add_all(assets)
        db.commit()
    finally:
        db.close()


def start_scheduler():
    # Set Scheduler to update lifecycle every new day
    scheduler = AsyncIOScheduler(timezone = UTC)
    scheduler.add_job(update_lifecycle, "cron", hour=0, minute=0)
    scheduler.start()
    return scheduler