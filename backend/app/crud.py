from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from . import models, schemas

def create_website(db: Session, website: schemas.WebsiteCreate):
    # db_website = models.Website(id=uuid4(), url=website.url, name=website.name)
    db_website = models.Website(
        id=uuid4(),
        url=str(website.url),  # 🔁 FIX: Convert HttpUrl to string
        name=website.name
    )
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website


    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website

def get_websites(db: Session):
    return db.query(models.Website).order_by(models.Website.created_at.desc()).all()

def delete_website(db: Session, website_id):
    db_website = db.query(models.Website).filter(models.Website.id == website_id).first()
    if db_website:
        db.delete(db_website)
        db.commit()
    return db_website

def create_scan_run(db: Session, website_id, report_path=None):
    db_scan = models.ScanRun(
        id=uuid4(),
        website_id=website_id,
        started_at=datetime.utcnow(),
        status="queued",
        report_path=report_path
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

def get_scan_runs(db: Session):
    return db.query(models.ScanRun).order_by(models.ScanRun.started_at.desc()).all()

def update_scan_status(db: Session, scan_id, status, report_path=None, parsed_result=None):
    scan = db.query(models.ScanRun).filter(models.ScanRun.id == scan_id).first()
    if scan:
        scan.status = status
        scan.completed_at = datetime.utcnow()
        if report_path:
            scan.report_path = report_path
        if parsed_result:
            scan.parsed_result = parsed_result
        db.commit()
        db.refresh(scan)
    return scan
