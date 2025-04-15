from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
import os
import subprocess
import json

from . import models, schemas, crud
from .database import SessionLocal, engine, Base

# Create tables (for dev, use Alembic for prod)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS for frontend ↔ backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/websites", response_model=list[schemas.Website])
def list_websites(db: Session = Depends(get_db)):
    return crud.get_websites(db)

@app.post("/websites", response_model=schemas.Website)
def add_website(website: schemas.WebsiteCreate, db: Session = Depends(get_db)):
    return crud.create_website(db, website)

@app.delete("/websites/{website_id}", response_model=schemas.Website)
def delete_website(website_id: UUID, db: Session = Depends(get_db)):
    deleted = crud.delete_website(db, website_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Website not found")
    return deleted

@app.post("/scan/{website_id}", response_model=schemas.ScanRun)
def trigger_scan(website_id: UUID, db: Session = Depends(get_db)):
    website = db.query(models.Website).filter(models.Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    scan = crud.create_scan_run(db, website_id)
    filename = f"zap_report_{scan.id}.json"
    report_path = f"data/reports/{filename}"

    # Trigger OWASP ZAP Scan (simplified blocking call)
    try:
        subprocess.run([
            "java", "-jar", "C:\\OWASP\\ZAP\\ZAP_2.16.1_Crossplatform\\ZAP_2.16.1\\zap-2.16.1.jar",
            "-cmd", "-quickurl", website.url,
            "-quickprogress", "-quickout", report_path
        ], check=True)

        with open(report_path, "r") as f:
            report_json = json.load(f)

        scan = crud.update_scan_status(
            db, scan.id, "success", report_path=report_path, parsed_result=report_json
        )

    except Exception as e:
        scan = crud.update_scan_status(db, scan.id, "failed")
        raise HTTPException(status_code=500, detail=f"ZAP scan failed: {str(e)}")

    return scan

@app.get("/scans", response_model=list[schemas.ScanRun])
def list_scans(db: Session = Depends(get_db)):
    return crud.get_scan_runs(db)

@app.get("/data/reports/{filename}")
def serve_report(filename: str):
    file_path = os.path.join("data", "reports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    with open(file_path, "r") as f:
        return json.load(f)
