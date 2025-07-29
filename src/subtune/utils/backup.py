import shutil

from ..config import BACKUP_SUFFIX


class BackupManager:
    """Utility for creating backup files before SRT modifications."""

    @staticmethod
    def create_backup(file_path):
        backup_path = file_path.with_suffix(file_path.suffix + BACKUP_SUFFIX)
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Warning: Could not create backup file: {e}")
            return None
