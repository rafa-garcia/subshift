from subtune.utils.backup import BackupManager


class TestBackupManager:
    def test_create_backup_success(self, tmp_path):
        original_file = tmp_path / "test.srt"
        original_content = "original content"
        original_file.write_text(original_content)

        backup_path = BackupManager.create_backup(original_file)

        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == original_content
        assert str(backup_path).endswith(".srt.backup")

    def test_create_backup_failure(self, tmp_path, capsys):
        nonexistent = tmp_path / "nonexistent.srt"

        backup_path = BackupManager.create_backup(nonexistent)

        assert backup_path is None
        captured = capsys.readouterr()
        assert "Warning: Could not create backup file" in captured.out
