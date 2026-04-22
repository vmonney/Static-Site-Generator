import os
import shutil


def copy_files_recursive(source_dir_path: str, dest_dir_path: str) -> None:
    """Recursively copy the contents of ``source_dir_path`` into ``dest_dir_path``.

    The destination directory is wiped clean first so the copy is deterministic.
    Subdirectories are walked recursively via ``os.listdir``/``os.path.isfile``.
    """
    if not os.path.exists(source_dir_path):
        raise FileNotFoundError(f"source path does not exist: {source_dir_path}")

    if os.path.exists(dest_dir_path):
        shutil.rmtree(dest_dir_path)
    os.mkdir(dest_dir_path)

    _copy_recursive(source_dir_path, dest_dir_path)


def _copy_recursive(source_dir_path: str, dest_dir_path: str) -> None:
    for entry in os.listdir(source_dir_path):
        source_path = os.path.join(source_dir_path, entry)
        dest_path = os.path.join(dest_dir_path, entry)
        print(f" * {source_path} -> {dest_path}")
        if os.path.isfile(source_path):
            shutil.copy(source_path, dest_path)
        else:
            os.mkdir(dest_path)
            _copy_recursive(source_path, dest_path)
