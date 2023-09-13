import zipfile
from pathlib import Path

import pytest

import cromshell.utilities.miniwdl_utils as miniwdl_utils


class TestMiniwdlUtilities:
    """Test miniwdl_utils  functions and variables"""

    def test_resolve_wdl_dependencies_zip(self, temp_dir):
        # Create a temporary ZIP file with some contents
        zip_path = Path(temp_dir).joinpath("test_dependencies.zip")
        with zipfile.ZipFile(zip_path, "w") as zip_ref:
            zip_ref.writestr("file1.wdl", "Test file 1 content")
            zip_ref.writestr("file2.wdl", "Test file 2 content")

        resolved_path = miniwdl_utils.resolve_wdl_dependencies(zip_path)
        assert Path(resolved_path).is_dir()
        assert "file1.wdl" in [item.name for item in Path(resolved_path).iterdir()]
        assert "file2.wdl" in [item.name for item in Path(resolved_path).iterdir()]

    def test_resolve_wdl_dependencies_directory(self, temp_dir):
        # Create a temporary directory with a dummy WDL file
        wdl_directory = Path(temp_dir).joinpath("test_directory")
        Path(wdl_directory).mkdir()
        with open(Path(wdl_directory).joinpath("dummy.wdl"), "w") as wdl_file:
            wdl_file.write("dummy WDL content")

        resolved_path = miniwdl_utils.resolve_wdl_dependencies(wdl_directory)
        assert Path(resolved_path).is_dir()
        assert "dummy.wdl" in [item.name for item in Path(resolved_path).iterdir()]

    def test_resolve_wdl_dependencies_invalid(self):
        with pytest.raises(FileNotFoundError):
            miniwdl_utils.resolve_wdl_dependencies("nonexistent_file_or_directory")
