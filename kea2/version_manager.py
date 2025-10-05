import json
from pathlib import Path
from importlib.metadata import version
from packaging.version import Version
from .utils import getLogger, getProjectRoot


logger = getLogger(__name__)


def find_new_config_files(src_dir, dst_dir):
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    
    if not src_path.exists():
        return []
    
    src_files = {f.relative_to(src_path) for f in src_path.rglob('*') if f.is_file()}
    dst_files = {f.relative_to(dst_path) for f in dst_path.rglob('*') if f.is_file()} if dst_path.exists() else set()
    
    new_files = [str(file_rel) for file_rel in src_files if file_rel not in dst_files]
    
    return new_files


def sanitize_version(args) :
    base_dir = getProjectRoot()
    configs_dir = base_dir / "configs"
    version_file = configs_dir / "version.json"
    
    version_config = "0.3.6"
    min_version = "0.3.6"
    max_version = "0.3.6"
    version_cur = version("Kea2-python")
    
    with open(version_file, 'r', encoding='utf-8') as f:
        version_info = json.load(f)
    version_config = (version_info.get("version") or "0.3.6")
    min_version = (version_info.get("min_version") or "0.3.6")
    max_version = (version_info.get("max_version") or "100.0.0")

    # if no_need_to_update:
    #     logger.info(f"The configuration file does not need to be updated.\n")
    #     return
    
    logger.error(
        f"Configuration update required!\n"
        f"Current Kea2 version: {version_cur}\n"
        f"Configs version: {version_config}\n"
        f"The currently applicable version range for the configuration file is from {min_version} to {max_version}.\n"
        f"Please update your configuration files."
    )
    src = Path(__file__).parent / "assets" / "fastbot_configs"
    new_files = find_new_config_files(src, configs_dir)
    if new_files:
        logger.info("\n🆕 List of newly added files:")
        for i, file_path in enumerate(new_files, 1):
            logger.info(f"   {i:2d}. {file_path}")
