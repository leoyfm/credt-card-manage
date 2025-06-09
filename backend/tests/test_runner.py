"""
统一测试运行器

提供统一的测试运行入口，支持选择性运行：
- 单元测试
- 集成测试  
- 性能测试
- 所有测试
"""

import os
import sys
import argparse
import subprocess
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_root = Path(__file__).parent
        
        # 测试配置
        self.test_configs = {
            "unit": {
                "description": "单元测试 (FastAPI TestClient)",
                "path": "tests/unit/",
                "pattern": "test_*_unit.py",
                "markers": "unit",
                "parallel": False,
                "coverage": True
            },
            "integration": {
                "description": "集成测试 (真实HTTP请求)",
                "path": "tests/integration/",
                "pattern": "test_*_integration.py", 
                "markers": "integration",
                "parallel": False,
                "coverage": False,
                "requires_server": True
            },
            "performance": {
                "description": "性能测试 (基准测试)",
                "path": "tests/performance/",
                "pattern": "test_*_performance.py",
                "markers": "performance",
                "parallel": False,
                "coverage": False,
                "timeout": 300
            },
            "legacy": {
                "description": "原有测试文件",
                "path": "tests/",
                "pattern": "test_*.py",
                "exclude_dirs": ["unit", "integration", "performance"],
                "markers": "legacy",
                "parallel": True,
                "coverage": True
            }
        }
    
    def _run_command(self, command: List[str], cwd: str = None, capture_output: bool = True) -> Dict[str, Any]:
        """运行命令并返回结果"""
        if cwd is None:
            cwd = str(self.project_root)
        
        logger.info(f"执行命令: {' '.join(command)}")
        logger.info(f"工作目录: {cwd}")
        
        try:
            # 设置环境变量解决Windows编码问题
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            if capture_output:
                # 捕获输出模式（用于服务器检查等）
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env,
                    timeout=600
                )
                
                return {
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "command": " ".join(command)
                }
            else:
                # 实时输出模式（用于测试执行）
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env,
                    bufsize=1,
                    universal_newlines=True
                )
                
                output_lines = []
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())  # 实时打印输出
                        output_lines.append(output.strip())
                
                returncode = process.poll()
                
                return {
                    "success": returncode == 0,
                    "returncode": returncode,
                    "stdout": "\n".join(output_lines),
                    "stderr": "",
                    "command": " ".join(command)
                }
                
        except subprocess.TimeoutExpired:
            logger.error("命令执行超时")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "命令执行超时",
                "command": " ".join(command)
            }
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(command)
            }
    
    def _check_server_running(self) -> bool:
        """检查服务器是否运行"""
        try:
            import requests
            # 首先尝试检查根路径或API路径
            urls_to_check = [
                "http://127.0.0.1:8000/",
                "http://127.0.0.1:8000/api/health",
                "http://127.0.0.1:8000/docs",
                "http://127.0.0.1:8000/api/"
            ]
            
            for url in urls_to_check:
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code in [200, 404]:  # 404也说明服务器在运行
                        logger.info(f"✅ 服务器健康检查成功: {url} -> {response.status_code}")
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"服务器健康检查失败: {e}")
            return False
    
    def _display_server_start_instructions(self):
        """显示服务器启动说明"""
        logger.info("🚀 集成测试需要服务器运行")
        logger.info("📝 请在另一个终端中执行以下命令启动服务器:")
        logger.info("   python start.py dev")
        logger.info("")
        logger.info("💡 启动服务器后，可以通过以下方式验证:")
        logger.info("   - 访问 http://127.0.0.1:8000/docs 查看API文档")
        logger.info("   - 或运行: python run_integration_manual.py")
    

    
    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """运行单元测试"""
        logger.info("🧪 运行单元测试...")
        
        config = self.test_configs["unit"]
        command = ["python", "-m", "pytest"]
        
        # 添加测试路径
        command.extend([config["path"]])
        
        # 添加标记（不使用-k参数，因为容易出错）
        command.extend(["-m", config["markers"]])
        
        # 并行执行
        if config.get("parallel", False):
            command.extend(["-n", "auto"])
        
        # 覆盖率报告
        if config.get("coverage", False):
            command.extend(["--cov=.", "--cov-report=term-missing"])
        
        # 详细输出
        if verbose:
            command.append("-v")
        
        return self._run_command(command, capture_output=False)
    
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """运行集成测试"""
        logger.info("🌐 运行集成测试...")
        
        config = self.test_configs["integration"]
        
        # 检查是否需要服务器运行
        if config.get("requires_server", False):
            if not self._check_server_running():
                logger.error("❌ 服务器未运行")
                logger.info("💡 集成测试需要服务器运行，请执行以下步骤:")
                logger.info("   1. 在另一个终端中启动服务器:")
                logger.info("      python start.py dev")
                logger.info("   2. 等待服务器完全启动")
                logger.info("   3. 重新运行集成测试:")
                logger.info("      python tests/test_runner.py integration")
                logger.info("")
                logger.info("🔍 或者使用手动集成测试脚本:")
                logger.info("      python run_integration_manual.py")
                
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": "服务器未运行，请手动启动服务器",
                    "command": "server check"
                }
            else:
                logger.info("✅ 服务器已在运行，开始执行集成测试")
        
        command = ["python", "-m", "pytest"]
        
        # 添加测试路径
        command.extend([config["path"]])
        
        # 添加标记（不使用-k参数，因为容易出错）
        command.extend(["-m", config["markers"]])
        
        # 不并行执行（集成测试可能有依赖）
        command.extend(["-x"])  # 遇到失败就停止
        
        # 详细输出
        if verbose:
            command.append("-v")
        
        return self._run_command(command, capture_output=False)
    
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info("⚡ 运行性能测试...")
        
        config = self.test_configs["performance"]
        command = ["python", "-m", "pytest"]
        
        # 添加测试路径
        command.extend([config["path"]])
        
        # 添加标记（不使用-k参数，因为容易出错）
        command.extend(["-m", config["markers"]])
        
        # 超时设置
        if config.get("timeout"):
            command.extend(["--timeout", str(config["timeout"])])
        
        # 不并行执行（性能测试需要独占资源）
        command.extend(["-x"])  # 遇到失败就停止
        
        # 详细输出
        if verbose:
            command.append("-v")
        
        return self._run_command(command, capture_output=False)
    
    def run_legacy_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """运行原有测试"""
        logger.info("📂 运行原有测试文件...")
        
        config = self.test_configs["legacy"]
        command = ["python", "-m", "pytest"]
        
        # 添加测试路径，排除新目录
        exclude_dirs = config.get("exclude_dirs", [])
        test_files = []
        
        for test_file in Path(config["path"]).glob(config["pattern"]):
            # 检查是否在排除目录中
            if not any(exclude_dir in str(test_file) for exclude_dir in exclude_dirs):
                test_files.append(str(test_file))
        
        if not test_files:
            logger.info("ℹ️  没有找到原有测试文件")
            return {
                "success": True,
                "returncode": 0,
                "stdout": "没有原有测试文件",
                "stderr": "",
                "command": "legacy test check"
            }
        
        command.extend(test_files)
        
        # 覆盖率报告
        if config.get("coverage", False):
            command.extend(["--cov=.", "--cov-report=term-missing"])
        
        # 详细输出
        if verbose:
            command.append("-v")
        
        return self._run_command(command, capture_output=False)
    
    def run_all_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("🚀 运行所有测试...")
        
        results = {}
        overall_success = True
        
        # 运行单元测试
        logger.info("\n" + "="*60)
        unit_result = self.run_unit_tests(verbose)
        results["unit"] = unit_result
        if not unit_result["success"]:
            overall_success = False
            logger.error("❌ 单元测试失败")
        else:
            logger.info("✅ 单元测试通过")
        
        # 运行原有测试
        logger.info("\n" + "="*60)
        legacy_result = self.run_legacy_tests(verbose)
        results["legacy"] = legacy_result
        if not legacy_result["success"]:
            overall_success = False
            logger.error("❌ 原有测试失败")
        else:
            logger.info("✅ 原有测试通过")
        
        # 运行集成测试
        logger.info("\n" + "="*60)
        integration_result = self.run_integration_tests(verbose)
        results["integration"] = integration_result
        if not integration_result["success"]:
            overall_success = False
            logger.error("❌ 集成测试失败")
        else:
            logger.info("✅ 集成测试通过")
        
        # 运行性能测试
        logger.info("\n" + "="*60)
        performance_result = self.run_performance_tests(verbose)
        results["performance"] = performance_result
        if not performance_result["success"]:
            overall_success = False
            logger.error("❌ 性能测试失败")
        else:
            logger.info("✅ 性能测试通过")
        
        # 汇总结果
        logger.info("\n" + "="*60)
        logger.info("📊 测试结果汇总:")
        for test_type, result in results.items():
            status = "✅" if result["success"] else "❌"
            config = self.test_configs.get(test_type, {})
            description = config.get("description", test_type)
            logger.info(f"   {status} {description}")
        
        return {
            "success": overall_success,
            "returncode": 0 if overall_success else 1,
            "results": results,
            "command": "run_all_tests"
        }
    
    def list_available_tests(self):
        """列出可用的测试"""
        logger.info("📋 可用测试类型:")
        
        for test_type, config in self.test_configs.items():
            logger.info(f"\n🔹 {test_type}:")
            logger.info(f"   描述: {config['description']}")
            logger.info(f"   路径: {config['path']}")
            logger.info(f"   模式: {config['pattern']}")
            
            if config.get("requires_server"):
                logger.info(f"   依赖: 需要运行服务器")
            
            if config.get("parallel"):
                logger.info(f"   执行: 并行")
            else:
                logger.info(f"   执行: 串行")
    
    def generate_test_report(self, results: Dict[str, Any]):
        """生成测试报告"""
        report_file = self.tests_root / "TEST_REPORT.md"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# 测试报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if "results" in results:
                # 汇总报告
                f.write("## 测试汇总\n\n")
                f.write("| 测试类型 | 状态 | 描述 |\n")
                f.write("|----------|------|------|\n")
                
                for test_type, result in results["results"].items():
                    status = "✅ 通过" if result["success"] else "❌ 失败"
                    config = self.test_configs.get(test_type, {})
                    description = config.get("description", test_type)
                    f.write(f"| {test_type} | {status} | {description} |\n")
                
                f.write("\n")
                
                # 详细结果
                for test_type, result in results["results"].items():
                    f.write(f"### {test_type} 详细结果\n\n")
                    f.write(f"**命令**: `{result['command']}`\n\n")
                    f.write(f"**返回码**: {result['returncode']}\n\n")
                    
                    if result["stdout"]:
                        f.write("**标准输出**:\n```\n")
                        f.write(result["stdout"])
                        f.write("\n```\n\n")
                    
                    if result["stderr"]:
                        f.write("**错误输出**:\n```\n")
                        f.write(result["stderr"])
                        f.write("\n```\n\n")
            else:
                # 单个测试报告
                f.write("## 测试结果\n\n")
                f.write(f"**状态**: {'✅ 通过' if results['success'] else '❌ 失败'}\n\n")
                f.write(f"**命令**: `{results['command']}`\n\n")
                
                if results["stdout"]:
                    f.write("**标准输出**:\n```\n")
                    f.write(results["stdout"])
                    f.write("\n```\n\n")
                
                if results["stderr"]:
                    f.write("**错误输出**:\n```\n")
                    f.write(results["stderr"])
                    f.write("\n```\n\n")
        
        logger.info(f"📄 测试报告已生成: {report_file}")

def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="信用卡管理系统测试运行器")
    parser.add_argument(
        "test_type",
        nargs="?",
        choices=["unit", "integration", "performance", "legacy", "all", "list"],
        default="all",
        help="要运行的测试类型"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    parser.add_argument(
        "-r", "--report",
        action="store_true",
        help="生成测试报告"
    )
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner()
    
    # 注册信号处理器
    import signal
    def cleanup_handler(signum, frame):
        logger.info("接收到退出信号，正在退出...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup_handler)  # Ctrl+C
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, cleanup_handler)  # 终止信号
    
    try:
        # 列出可用测试
        if args.test_type == "list":
            runner.list_available_tests()
            return
        
        # 运行测试
        result = None
        if args.test_type == "unit":
            result = runner.run_unit_tests(args.verbose)
        elif args.test_type == "integration":
            result = runner.run_integration_tests(args.verbose)
        elif args.test_type == "performance":
            result = runner.run_performance_tests(args.verbose)
        elif args.test_type == "legacy":
            result = runner.run_legacy_tests(args.verbose)
        elif args.test_type == "all":
            result = runner.run_all_tests(args.verbose)
        
        # 生成报告
        if args.report and result:
            from datetime import datetime
            runner.generate_test_report(result)
        
        # 退出码
        if result:
            exit_code = 0 if result["success"] else 1
        else:
            exit_code = 1
            
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        exit_code = 1
    except Exception as e:
        logger.error(f"测试运行失败: {e}")
        exit_code = 1
        
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 