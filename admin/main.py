from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import math
from contextlib import asynccontextmanager
from .logger import log

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Admin server starting up...")
    yield
    log.info("Admin server shutting down...")

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="admin/static"), name="static")

templates = Jinja2Templates(directory="admin/templates")

def get_db_connection():
    conn = sqlite3.connect('db/rag.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/crawl_jobs", response_class=HTMLResponse)
async def crawl_jobs_page(request: Request):
    return templates.TemplateResponse("crawl_jobs.html", {"request": request})

@app.get("/crawled_pages", response_class=HTMLResponse)
async def crawled_pages_page(request: Request):
    return templates.TemplateResponse("crawled_pages.html", {"request": request})

@app.get("/ingestion_jobs", response_class=HTMLResponse)
async def ingestion_jobs_page(request: Request):
    return templates.TemplateResponse("ingestion_jobs.html", {"request": request})

@app.get("/ingested_documents", response_class=HTMLResponse)
async def ingested_documents_page(request: Request):
    return templates.TemplateResponse("ingested_documents.html", {"request": request})

def build_where_clause(params):
    conditions = []
    values = []
    for key, value in params.items():
        if value:
            conditions.append(f"{key} LIKE ?")
            values.append(f"%{value}%")
    return " AND ".join(conditions), values

@app.get("/api/crawl_jobs")
def get_crawl_jobs(page: int = 1, size: int = 10, status: str = None):
    conn = get_db_connection()
    offset = (page - 1) * size
    
    where_clause, values = build_where_clause({'status': status})
    
    query = 'SELECT * FROM crawl_jobs'
    count_query = 'SELECT COUNT(*) FROM crawl_jobs'
    
    if where_clause:
        query += f' WHERE {where_clause}'
        count_query += f' WHERE {where_clause}'

    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    
    total = conn.execute(count_query, values).fetchone()[0]
    jobs = conn.execute(query, (*values, size, offset)).fetchall()
    conn.close()
    
    return JSONResponse(content={
        "total": total,
        "page": page,
        "size": size,
        "total_pages": math.ceil(total / size),
        "items": [dict(row) for row in jobs]
    })

@app.get("/api/crawled_pages")
def get_crawled_pages(page: int = 1, size: int = 10, url: str = None):
    conn = get_db_connection()
    offset = (page - 1) * size
    
    where_clause, values = build_where_clause({'url': url})
    
    query = 'SELECT * FROM crawled_pages'
    count_query = 'SELECT COUNT(*) FROM crawled_pages'
    
    if where_clause:
        query += f' WHERE {where_clause}'
        count_query += f' WHERE {where_clause}'

    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'

    total = conn.execute(count_query, values).fetchone()[0]
    pages = conn.execute(query, (*values, size, offset)).fetchall()
    conn.close()
    
    return JSONResponse(content={
        "total": total,
        "page": page,
        "size": size,
        "total_pages": math.ceil(total / size),
        "items": [dict(row) for row in pages]
    })

@app.get("/api/ingestion_jobs")
def get_ingestion_jobs(page: int = 1, size: int = 10, status: str = None, source_type: str = None):
    conn = get_db_connection()
    offset = (page - 1) * size
    
    where_clause, values = build_where_clause({'status': status, 'source_type': source_type})

    query = 'SELECT * FROM ingestion_jobs'
    count_query = 'SELECT COUNT(*) FROM ingestion_jobs'

    if where_clause:
        query += f' WHERE {where_clause}'
        count_query += f' WHERE {where_clause}'

    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    
    total = conn.execute(count_query, values).fetchone()[0]
    jobs = conn.execute(query, (*values, size, offset)).fetchall()
    conn.close()
    
    return JSONResponse(content={
        "total": total,
        "page": page,
        "size": size,
        "total_pages": math.ceil(total / size),
        "items": [dict(row) for row in jobs]
    })

@app.get("/api/ingested_documents")
def get_ingested_documents(page: int = 1, size: int = 10, status: str = None, source_type: str = None, vector_id: str = None):
    conn = get_db_connection()
    offset = (page - 1) * size
    
    where_clause, values = build_where_clause({'status': status, 'source_type': source_type, 'vector_id': vector_id})

    query = 'SELECT * FROM ingested_documents'
    count_query = 'SELECT COUNT(*) FROM ingested_documents'

    if where_clause:
        query += f' WHERE {where_clause}'
        count_query += f' WHERE {where_clause}'

    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    
    total = conn.execute(count_query, values).fetchone()[0]
    documents = conn.execute(query, (*values, size, offset)).fetchall()
    conn.close()
    
    return JSONResponse(content={
        "total": total,
        "page": page,
        "size": size,
        "total_pages": math.ceil(total / size),
        "items": [dict(row) for row in documents]
    })
