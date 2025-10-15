from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from utils.database import get_db
from utils.keycloak import validate_access_token
from typing import Dict, Any, List
import json
from datetime import datetime

router = APIRouter(prefix="/database", tags=["Database"])  # ลบ /api ออก

@router.get("/tables")
async def get_all_tables(
    db: AsyncSession = Depends(get_db),
    user_data: dict = Depends(validate_access_token)
):
    """ดึงรายชื่อตารางทั้งหมดใน database"""
    try:
        # ดึงรายชื่อตารางทั้งหมด
        result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        return {
            "success": True,
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")

@router.get("/table/{table_name}")
async def get_table_data(
    table_name: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user_data: dict = Depends(validate_access_token)
):
    """ดึงข้อมูลจากตารางที่ระบุ"""
    try:
        # ตรวจสอบว่าตารางมีอยู่จริง
        table_check = await db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = :table_name
            )
        """), {"table_name": table_name})
        
        if not table_check.scalar():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # ดู columns ก่อน (ไม่ต้องใช้ ORDER BY id ถ้าไม่มี id)
        columns_result = await db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = :table_name
            ORDER BY ordinal_position
        """), {"table_name": table_name})
        
        column_names = [row[0] for row in columns_result.fetchall()]
        
        # ดึงข้อมูลจากตาราง (ไม่ ORDER BY id)
        result = await db.execute(text(f"""
            SELECT * FROM {table_name} 
            LIMIT :limit OFFSET :offset
        """), {"limit": limit, "offset": offset})
        
        rows = result.fetchall()
        
        # แปลงเป็น list of dict
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(column_names):
                value = row[i] if i < len(row) else None
                # แปลง datetime เป็น string
                if isinstance(value, datetime):
                    value = value.isoformat()
                row_dict[col] = value
            data.append(row_dict)
        
        # นับจำนวนรายการทั้งหมด
        count_result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total_count = count_result.scalar()
        
        return {
            "success": True,
            "table_name": table_name,
            "data": data,
            "columns": column_names,
            "count": len(data),
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@router.get("/person")
async def get_all_persons(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user_data: dict = Depends(validate_access_token)
):
    """ดึงข้อมูล person ทั้งหมด"""
    try:
        # ใช้ชื่อตารางที่ถูกต้อง - อาจจะเป็น person หรือ yott_person
        result = await db.execute(text("""
            SELECT uid, preferred_username, given_name, family_name, email, created_at, updated_at
            FROM person 
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """), {"limit": limit, "offset": offset})
        
        rows = result.fetchall()
        
        persons = []
        for row in rows:
            persons.append({
                "uid": row[0],
                "username": row[1],
                "given_name": row[2],
                "family_name": row[3],
                "display_name": f"{row[2] or ''} {row[3] or ''}".strip() or row[1],
                "email": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })
        
        # นับจำนวนทั้งหมด
        count_result = await db.execute(text("SELECT COUNT(*) FROM person"))
        total_count = count_result.scalar()
        
        return {
            "success": True,
            "persons": persons,
            "count": len(persons),
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching persons: {str(e)}")