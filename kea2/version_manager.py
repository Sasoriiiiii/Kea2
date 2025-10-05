import json
from pathlib import Path
from packaging.version import Version
from .utils import getLogger, getProjectRoot
from typing import List, Optional
import shutil
from importlib.metadata import version
from dataclasses import dataclass


logger = getLogger(__name__)

@dataclass
class ConfigVersionRange:
    name: str
    description: str
    min_version: str
    max_version: str

    def contains(self, ver: str) -> bool:
        return Version(self.min_version) <= Version(ver) <= Version(self.max_version)


def find_new_config_files(src_dir, dst_dir):
    """将src_dir中新增文件添加到dst_dir中"""
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    
    if not src_path.exists():
        return []
    
    src_files = {f.relative_to(src_path) for f in src_path.rglob('*') if f.is_file()}
    dst_files = {f.relative_to(dst_path) for f in dst_path.rglob('*') if f.is_file()} if dst_path.exists() else set()
    
    files_to_copy  = [file_rel for file_rel in src_files if file_rel not in dst_files]
    
    copied_files = []
    for file_rel in files_to_copy:
        src_file = src_path / file_rel
        dst_file = dst_path / file_rel
        
        try:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_file, dst_file)
            copied_files.append(str(file_rel))
            
            logger.info(f"新增配置文件: {file_rel}")
            
        except Exception as e:
            logger.error(f"新增配置文件失败 {file_rel}: {e}")
    logger.info(f"总共新增了 {len(copied_files)} 个文件")
    
    return copied_files

class SanitizeConfigVersion :
    def __init__(self, project_config_path:str, user_config_path:str):
        """
        初始化
        
        Args:
            project_config_path: 项目配置文件路径
            user_config_path: 用户配置文件路径
            config_version: 用户配置文件版本
            project_version: 项目版本
            config_version_ranges: 适用的配置文件版本区间
        """
        self.project_config_path = project_config_path
        self.user_config_path = user_config_path
        self.project_version = version("Kea2-python")
        self.config_version=""
        self.config_version_ranges: List[ConfigVersionRange] = []
        self._load_config()
        
    
    def _load_config(self) ->None:
        """从JSON文件中加载版本区间与用户配置文件版本"""
        
        if (self.user_config_path/"version.json").exists():
            with open(self.user_config_path/"version.json", 'r', encoding='utf-8') as f:
                user_config_data = json.load(f)
            self.config_version = user_config_data.get("config_version")
        else:
            self.config_version = "0.3.5"
            
        with open(self.project_config_path/"version.json", 'r', encoding='utf-8') as f:
            project_config_data = json.load(f)
        
        for range_data in project_config_data.get("config_version_ranges",[]):
            version_range = ConfigVersionRange(
                name=range_data['name'],
                description=range_data['description'],
                min_version=range_data['min_version'],
                max_version=range_data['max_version'],
            )
            self.config_version_ranges.append(version_range)
            
    def get_current_version_range(self) -> Optional[ConfigVersionRange]:
        """获取当前软件版本适用的版本区间"""
        for version_range in self.config_version_ranges:
            if version_range.contains(self.project_version):
                return version_range
        return None
    
    def check_config_compatibility(self):
        """检测用户配置文件版本是否在适配的区间中"""
        accept_range = self.get_current_version_range()
        if Version(accept_range.min_version) <= Version(self.config_version) <= Version(accept_range.max_version):
            return
        logger.error(
            f"Configuration update required!\n"
            f"Current Kea2 version: {self.project_version}\n"
            f"Configs version: {self.config_version}\n"
            f"The currently applicable version range for the configuration file is from {accept_range.min_version} to {accept_range.max_version}.\n"
            f"Please update your configuration files."
        )
        find_new_config_files(self.project_config_path, self.user_config_path)