from ..utils.backup import BackupManager
from .validator import FileValidator


class SubtitleProcessor:
    """Main service orchestrator for SRT subtitle processing operations."""

    def __init__(self):
        self.validator = FileValidator()
        self.backup_manager = BackupManager()

    def shift_srt_file(self, input_path, output_path, offset_ms, create_backup=False):
        self.validator.validate_input_file(input_path)
        self.validator.check_file_warnings(input_path)
        self.validator.validate_output_location(output_path)

        offset = self.validator.validate_offset(offset_ms)

        backup_path = None
        if create_backup:
            backup_path = self.backup_manager.create_backup(input_path)
            if backup_path:
                print(f"Created backup: {backup_path}")

        srt_file = self.validator.read_srt_file(input_path)
        shifted_srt = self._shift_subtitles(srt_file, offset)
        self.validator.write_srt_file(shifted_srt, output_path)

        subtitle_count = len(shifted_srt)
        print(f"Successfully processed {subtitle_count} subtitles")

        return subtitle_count

    @staticmethod
    def _shift_subtitles(srt_file, offset):
        return srt_file.shift(offset)
