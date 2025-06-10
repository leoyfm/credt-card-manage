"""测试环境管理工具

管理测试环境配置和状态
"""

import os
import requests
from typing import Dict, Any, Optional
from pathlib import Path


class TestEnvironment:
    """测试环境管理器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.is_server_running = None
        self._check_cache = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """加载测试配置"""
        return {
            "api_base_url": os.getenv("TEST_API_BASE_URL", "http://127.0.0.1:8000"),
            "database_url": os.getenv("TEST_DATABASE_URL", "postgresql://test:test@localhost/test_db"),
            "cleanup_data": os.getenv("TEST_CLEANUP_DATA", "true").lower() == "true",
            "timeout": int(os.getenv("TEST_TIMEOUT", "30")),
            "max_retries": int(os.getenv("TEST_MAX_RETRIES", "3")),
            "log_level": os.getenv("TEST_LOG_LEVEL", "INFO"),
            "parallel_tests": os.getenv("TEST_PARALLEL", "false").lower() == "true"
        }
    
    def get_api_base_url(self) -> str:
        """获取API基础URL"""
        return self.config["api_base_url"]
    
    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.config["database_url"]
    
    def should_cleanup_data(self) -> bool:
        """是否应该清理测试数据"""
        return self.config["cleanup_data"]
    
    def get_timeout(self) -> int:
        """获取请求超时时间"""
        return self.config["timeout"]
    
    def is_parallel_enabled(self) -> bool:
        """是否启用并行测试"""
        return self.config["parallel_tests"]
    
    def check_server_running(self, force_check: bool = False) -> bool:
        """检查服务器是否运行"""
        if not force_check and self.is_server_running is not None:
            return self.is_server_running
        
        try:
            url = f"{self.get_api_base_url()}/api/v1/public/system/health"
            response = requests.get(url, timeout=5)
            self.is_server_running = response.status_code == 200
            
            if self.is_server_running:
                print(f"✅ 服务器运行正常: {self.get_api_base_url()}")
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.is_server_running = False
            print(f"❌ 服务器连接失败: {e}")
            print(f"\n请确保服务器已启动:")
            print(f"  cd backend && python start.py dev")
            print(f"  或: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
        return self.is_server_running
    
    def wait_for_server(self, max_attempts: int = 30, interval: int = 2) -> bool:
        """等待服务器启动"""
        import time
        
        print(f"等待服务器启动... (最多等待 {max_attempts * interval} 秒)")
        
        for attempt in range(max_attempts):
            if self.check_server_running(force_check=True):
                return True
            
            print(f"  尝试 {attempt + 1}/{max_attempts}，{interval}秒后重试...")
            time.sleep(interval)
        
        return False
    
    def get_test_data_dir(self) -> Path:
        """获取测试数据目录"""
        return Path(__file__).parent.parent.parent / "data"
    
    def get_config_dir(self) -> Path:
        """获取配置目录"""
        return Path(__file__).parent.parent.parent / "config"
    
    def load_fixture(self, name: str) -> Dict[str, Any]:
        """加载测试固定数据"""
        fixture_path = self.get_test_data_dir() / "fixtures" / f"{name}.json"
        if fixture_path.exists():
            import json
            with open(fixture_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_env_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        return {
            "api_base_url": self.get_api_base_url(),
            "database_url": self.get_database_url().replace("://", "://***:***@").split("@")[1] if "@" in self.get_database_url() else self.get_database_url(),
            "cleanup_data": self.should_cleanup_data(),
            "timeout": self.get_timeout(),
            "parallel_tests": self.is_parallel_enabled(),
            "server_running": self.check_server_running(),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "test_data_dir": str(self.get_test_data_dir()),
            "config_dir": str(self.get_config_dir())
        }
    
    def print_env_info(self):
        """打印环境信息"""
        info = self.get_env_info()
        print("\n🔧 测试环境信息:")
        print("=" * 50)
        for key, value in info.items():
            print(f"  {key}: {value}")
        print("=" * 50) 