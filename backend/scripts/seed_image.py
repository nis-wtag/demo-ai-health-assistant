import json
from pathlib import Path

from core.database import SessionLocal
from models.doctor import Doctor
from sqlalchemy.future import select
from sqlalchemy.orm import Session

DATA_DIR = Path(__file__).parent.parent / "data" / "doctors" / "info"


def seed_images_only():
    """
    Update existing doctors with the 'image' field from JSON files.
    """
    print("--- Starting Image Update Process ---")
    if not DATA_DIR.exists():
        print(f"Error: Data directory not found at '{DATA_DIR}'")
        return

    db: Session = SessionLocal()
    json_files = list(DATA_DIR.glob("*.json"))
    total_files = len(json_files)
    updated_count = 0
    skipped_count = 0

    try:
        for idx, file_path in enumerate(json_files, start=1):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    doctor_data = json.load(f)

                doctor_name = doctor_data.get("name")
                image_path = doctor_data.get("image")  # New field
                if not doctor_name or not image_path:
                    skipped_count += 1
                    continue

                stmt = select(Doctor).where(Doctor.full_name == doctor_name)
                db_doctor = db.execute(stmt).scalar_one_or_none()

                if not db_doctor:
                    skipped_count += 1
                    continue

                db_doctor.image = image_path
                db.add(db_doctor)
                updated_count += 1

                if idx % 50 == 0:
                    print(f"Progress: {idx}/{total_files} files processed.")

            except Exception as e:
                print(f"Error processing file {file_path.name}: {e}")
                db.rollback()

        db.commit()
        print("\n--- Image Update Summary ---")
        print(f"Total files: {total_files}")
        print(f"Images updated: {updated_count}")
        print(f"Skipped (no doctor found or no image): {skipped_count}")
        print("-----------------------------")

    finally:
        db.close()


if __name__ == "__main__":
    seed_images_only()
