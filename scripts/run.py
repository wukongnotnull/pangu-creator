#!/usr/bin/env python3
"""
盘古造物信息采集入口

自动检测 Python 环境：
- 有 Python + uv → uv run（推荐，自动管理依赖）
- 有 Python 无 uv → pip install 后运行
- 无 Python → 提示安装
"""

import subprocess
import sys
import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "cli.py")


def check_command(cmd: str) -> bool:
    """检测命令是否存在"""
    return shutil.which(cmd) is not None


def check_python() -> bool:
    """检测 Python 是否可用"""
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_with_uv(args: list):
    """使用 uv 运行"""
    result = subprocess.run(
        ["uv", "run", "--python", "3.9", "python", MAIN_SCRIPT] + args,
        cwd=SCRIPT_DIR,
    )
    return result.returncode


def run_with_pip(args: list):
    """使用 pip 安装依赖后运行"""
    print("📦 安装依赖...")
    install_result = subprocess.run(
        ["pip", "install", "-e", "."],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if install_result.returncode != 0:
        print(f"❌ 安装失败: {install_result.stderr}")
        return 1

    result = subprocess.run(
        ["python", MAIN_SCRIPT] + args,
        cwd=SCRIPT_DIR,
    )
    return result.returncode


def main():
    args = sys.argv[1:]

    if not args:
        # 无参数，显示帮助
        args = ["--help"]

    # 检查 uv
    if check_command("uv"):
        print("🔧 使用 uv 运行...")
        return run_with_uv(args)

    # 检查 Python
    if check_python():
        print("🔧 使用 pip 运行...")
        return run_with_pip(args)

    # 无 Python
    print("=" * 60)
    print("❌ 未检测到 Python 3.9+ 环境")
    print()
    print("请先安装 Python：")
    print()
    print("macOS/Linux:")
    print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
    print()
    print("Windows:")
    print('  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"')
    print()
    print("安装 uv 后，一条命令运行：")
    print("  uv run python run.py search \"芒格 思维框架\"")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
