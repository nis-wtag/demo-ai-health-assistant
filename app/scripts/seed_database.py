import json
from datetime import time
from pathlib import Path

from core.database import SessionLocal
from models.chamber import Chamber
from models.doctor import Doctor
from models.doctor_chamber import DAY, DoctorChamber, DoctorChamberVisitingHour
from sqlalchemy.future import select
from sqlalchemy.orm import Session

DATA_DIR = Path(__file__).parent.parent / "data" / "doctors" / "info"


def seed_database():
    """
    Populates the database by reading individual JSON files from a directory.
    This script is synchronous and idempotent.
    """
    print("--- Starting Database Seeding Process ---")
    if not DATA_DIR.exists():
        print(f"Error: Data directory not found at '{DATA_DIR}'")
        return

    db: Session = SessionLocal()

    json_files = list(DATA_DIR.glob("*.json"))
    total_files = len(json_files)
    print(f"Found {total_files} JSON files to process.")

    chamber_cache = {}  # Cache to avoid duplicate chamber lookups
    processed_count = 0
    success_count = 0
    failed_count = 0

    try:
        for file_path in json_files:
            processed_count += 1
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    doctor_data = json.load(f)

                # Each doctor is processed in its own transaction.
                with db.begin():
                    doctor_name = doctor_data.get("name")
                    if not doctor_name:
                        raise ValueError("Doctor name is missing in JSON.")

                    stmt = select(Doctor).where(Doctor.full_name == doctor_name)
                    db_doctor = db.execute(stmt).scalar_one_or_none()

                    if db_doctor:
                        continue

                    print(
                        f"Processing ({processed_count}/{total_files}): {doctor_name}"
                    )
                    db_doctor = Doctor(
                        full_name=doctor_name,
                        degrees=doctor_data.get("degree"),
                        specialization=doctor_data.get("speciality"),
                        designation=doctor_data.get("designation"),
                        affiliated_hospital=doctor_data.get("workplace"),
                    )
                    db.add(db_doctor)
                    db.flush()

                    for chamber_info in doctor_data.get("chambers", []):
                        chamber_name = chamber_info.get("place")
                        if not chamber_name:
                            continue

                        chamber = chamber_cache.get(chamber_name)
                        if not chamber:
                            stmt = select(Chamber).where(
                                Chamber.chamber_name == chamber_name
                            )
                            chamber = db.execute(stmt).scalar_one_or_none()

                            if not chamber:
                                address_data = chamber_info.get("address", {})
                                chamber = Chamber(
                                    chamber_name=chamber_name,
                                    address=address_data.get("name"),
                                    longitude=address_data.get("longitude"),
                                    latitude=address_data.get("latitude"),
                                )
                                db.add(chamber)
                                db.flush()
                            chamber_cache[chamber_name] = chamber

                        doctor_chamber = DoctorChamber(
                            doctor_id=db_doctor.id,
                            chamber_id=chamber.id,
                            contact_number=chamber_info.get("contact"),
                        )
                        db.add(doctor_chamber)
                        db.flush()

                        for hour_info in chamber_info.get("visiting_hours", []):
                            day_str = hour_info.get("day", "").upper()
                            if not day_str or day_str not in DAY.__members__:
                                continue

                            start_time_str = hour_info.get("start_time")
                            end_time_str = hour_info.get("end_time")

                            visiting_hour = DoctorChamberVisitingHour(
                                doctor_chamber_id=doctor_chamber.id,
                                day=DAY[day_str],
                                start_time=time.fromisoformat(start_time_str)
                                if start_time_str
                                else None,
                                end_time=time.fromisoformat(end_time_str)
                                if end_time_str
                                else None,
                            )
                            db.add(visiting_hour)

                success_count += 1
                if processed_count % 100 == 0:
                    print(f"Progress: {processed_count}/{total_files} files processed.")

            except Exception as e:
                failed_count += 1
                print(f"Error processing file {file_path.name}: {e}")
                db.rollback()

        db.commit()

    finally:
        db.close()
        print("\n--- Seeding Process Summary ---")
        print(f"Total files found: {total_files}")
        print(f"Successfully processed (created): {success_count}")
        print(f"Skipped (already exist): {total_files - success_count - failed_count}")
        print(f"Failed to process: {failed_count}")
        print("---------------------------------")


if __name__ == "__main__":
    seed_database()
