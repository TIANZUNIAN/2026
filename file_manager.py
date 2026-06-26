#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地文件管理工具
功能：文件统计、图片批量重命名、大文件报告、空文件夹清理
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# ==================== 常量配置 ====================

# 常见图片后缀（统一小写比较）
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".tiff", ".tif", ".svg", ".ico",
}

# 按类别统计的后缀分组
EXTENSION_CATEGORIES: Dict[str, Tuple[str, ...]] = {
    "Python": (".py", ".pyw", ".ipynb"),
    "Markdown": (".md", ".markdown"),
    "文本": (".txt", ".log", ".csv"),
    "HTML": (".html", ".htm", ".xhtml"),
    "图片": tuple(IMAGE_EXTENSIONS),
    "文档": (".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"),
    "压缩包": (".zip", ".rar", ".7z", ".tar", ".gz"),
    "音视频": (".mp3", ".mp4", ".avi", ".mkv", ".wav", ".flac"),
}

# 默认大文件阈值：10 MB
DEFAULT_SIZE_THRESHOLD_MB = 10


# ==================== 工具函数 ====================

def validate_directory(path_str: str) -> Path:
    """
    校验并返回合法的目录 Path 对象。

    参数:
        path_str: 用户传入的文件夹路径字符串

    返回:
        合法的 Path 对象

    异常:
        路径不存在或不是目录时抛出 ValueError
    """
    target = Path(path_str).expanduser().resolve()

    if not target.exists():
        raise ValueError(f"路径不存在: {target}")
    if not target.is_dir():
        raise ValueError(f"不是文件夹: {target}")

    return target


def format_size(size_bytes: int) -> str:
    """
    将字节数格式化为人类可读字符串。

    参数:
        size_bytes: 文件大小（字节）

    返回:
        如 "15.32 MB" 的字符串
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"


def iter_all_files(root: Path) -> List[Path]:
    """
    递归遍历目录，收集所有文件（不含目录本身）。

    参数:
        root: 根目录

    返回:
        所有文件的 Path 列表
    """
    files: List[Path] = []

    for dirpath, _, filenames in os.walk(root):
        current_dir = Path(dirpath)
        for filename in filenames:
            files.append(current_dir / filename)

    return files


def classify_extension(suffix: str) -> str:
    """
    根据后缀名返回所属分类名称。

    参数:
        suffix: 文件后缀（含点，如 .py）

    返回:
        分类名，未匹配则返回 "其他"
    """
    suffix = suffix.lower()

    for category, extensions in EXTENSION_CATEGORIES.items():
        if suffix in extensions:
            return category

    return "其他"


# ==================== 功能 1：文件统计 ====================

def scan_directory_stats(root: Path) -> Dict[str, int]:
    """
    批量遍历文件夹，统计文件总数及各类后缀数量。

    参数:
        root: 目标根目录

    返回:
        统计结果字典，键为分类名，值为数量
    """
    all_files = iter_all_files(root)
    stats: Dict[str, int] = defaultdict(int)

    stats["文件总数"] = len(all_files)

    for file_path in all_files:
        category = classify_extension(file_path.suffix)
        stats[category] += 1

    return dict(stats)


def print_scan_report(stats: Dict[str, int]) -> None:
    """
    在控制台打印文件统计报告。

    参数:
        stats: scan_directory_stats 返回的统计字典
    """
    print("\n" + "=" * 50)
    print("📊 文件统计报告")
    print("=" * 50)

    # 先打印总数，再按固定顺序打印各类别
    print(f"文件总数: {stats.get('文件总数', 0)}")
    print("-" * 50)

    ordered_keys = list(EXTENSION_CATEGORIES.keys()) + ["其他"]
    for key in ordered_keys:
        count = stats.get(key, 0)
        if count > 0:
            print(f"{key:<8}: {count}")

    print("=" * 50 + "\n")


# ==================== 功能 2：图片批量重命名 ====================

def collect_image_files(root: Path) -> List[Path]:
    """
    收集目录下所有图片文件。

    参数:
        root: 目标根目录

    返回:
        按路径排序后的图片文件列表
    """
    images = [
        f for f in iter_all_files(root)
        if f.suffix.lower() in IMAGE_EXTENSIONS
    ]
    # 按相对路径排序，保证重命名顺序稳定
    images.sort(key=lambda p: str(p.relative_to(root)).lower())
    return images


def rename_images_sequentially(
    root: Path,
    prefix: str = "image",
    start_index: int = 1,
    dry_run: bool = False,
) -> int:
    """
    将文件夹内所有图片重命名为 image_001、image_002 格式。

    采用两阶段重命名，避免文件名冲突。

    参数:
        root: 目标根目录
        prefix: 文件名前缀，默认 "image"
        start_index: 起始编号，默认 1
        dry_run: True 时只预览不实际修改

    返回:
        成功重命名的文件数量
    """
    images = collect_image_files(root)

    if not images:
        print("未找到任何图片文件。")
        return 0

    print(f"\n找到 {len(images)} 个图片文件，准备重命名...\n")

    # 第一阶段：全部改为临时名，避免与目标名冲突
    temp_mapping: List[Tuple[Path, Path]] = []
    for idx, src in enumerate(images, start=start_index):
        temp_name = src.parent / f"__temp_rename_{idx:03d}{src.suffix.lower()}"
        temp_mapping.append((src, temp_name))

    if dry_run:
        for idx, (src, _) in enumerate(temp_mapping, start=start_index):
            final_name = src.parent / f"{prefix}_{idx:03d}{src.suffix.lower()}"
            print(f"[预览] {src.relative_to(root)}  ->  {final_name.relative_to(root)}")
        return len(temp_mapping)

    # 执行临时重命名
    for src, temp in temp_mapping:
        src.rename(temp)

    # 第二阶段：临时名改为最终名
    renamed_count = 0
    for idx, (_, temp) in enumerate(temp_mapping, start=start_index):
        final_name = temp.parent / f"{prefix}_{idx:03d}{temp.suffix.lower()}"
        temp.rename(final_name)
        print(f"✔ {final_name.relative_to(root)}")
        renamed_count += 1

    print(f"\n共重命名 {renamed_count} 个图片文件。\n")
    return renamed_count


# ==================== 功能 3：大文件筛选 ====================

def find_large_files(
    root: Path,
    threshold_mb: float = DEFAULT_SIZE_THRESHOLD_MB,
    report_path: Path | None = None,
) -> List[Tuple[Path, int]]:
    """
    筛选大于指定大小（MB）的文件，并保存清单到 report.txt。

    参数:
        root: 目标根目录
        threshold_mb: 大小阈值（MB），默认 10
        report_path: 报告输出路径，默认为 root/report.txt

    返回:
        (文件路径, 字节大小) 的列表，按大小降序排列
    """
    threshold_bytes = int(threshold_mb * 1024 * 1024)
    large_files: List[Tuple[Path, int]] = []

    for file_path in iter_all_files(root):
        try:
            size = file_path.stat().st_size
        except OSError as exc:
            print(f"无法读取文件大小，已跳过: {file_path} ({exc})")
            continue

        if size > threshold_bytes:
            large_files.append((file_path, size))

    # 按大小从大到小排序
    large_files.sort(key=lambda item: item[1], reverse=True)

    if report_path is None:
        report_path = root / "report.txt"

    write_large_files_report(root, large_files, threshold_mb, report_path)

    print(f"\n发现 {len(large_files)} 个大文件（>{threshold_mb} MB）")
    print(f"报告已保存至: {report_path.resolve()}\n")

    return large_files


def write_large_files_report(
    root: Path,
    large_files: List[Tuple[Path, int]],
    threshold_mb: float,
    report_path: Path,
) -> None:
    """
    将大文件清单写入 report.txt。

    参数:
        root: 扫描根目录（用于计算相对路径）
        large_files: 大文件列表
        threshold_mb: 阈值（MB）
        report_path: 输出文件路径
    """
    lines = [
        "大文件扫描报告",
        "=" * 60,
        f"扫描目录: {root}",
        f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"大小阈值: > {threshold_mb} MB",
        f"大文件数量: {len(large_files)}",
        "=" * 60,
        "",
    ]

    if not large_files:
        lines.append("未发现超过阈值的大文件。")
    else:
        lines.append(f"{'序号':<6}{'大小':<14}{'相对路径'}")
        lines.append("-" * 60)

        for index, (file_path, size) in enumerate(large_files, start=1):
            rel_path = file_path.relative_to(root)
            lines.append(f"{index:<6}{format_size(size):<14}{rel_path}")

    report_path.write_text("\n".join(lines), encoding="utf-8")


# ==================== 功能 4：删除空文件夹 ====================

def remove_empty_directories(root: Path, dry_run: bool = False) -> int:
    """
    递归删除文件夹内的空目录（自底向上，避免误删仍有内容的父目录）。

    参数:
        root: 目标根目录
        dry_run: True 时只预览不实际删除

    返回:
        删除的空文件夹数量
    """
    removed_count = 0

    # topdown=False：从最深子目录开始向上处理
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        current = Path(dirpath)

        # 不删除根目录本身
        if current == root:
            continue

        # 再次确认目录为空（walk 过程中可能已删除子目录）
        try:
            is_empty = not any(current.iterdir())
        except OSError:
            continue

        if is_empty:
            if dry_run:
                print(f"[预览删除] {current.relative_to(root)}")
            else:
                current.rmdir()
                print(f"✔ 已删除空文件夹: {current.relative_to(root)}")
            removed_count += 1

    print(f"\n共 {'将删除' if dry_run else '已删除'} {removed_count} 个空文件夹。\n")
    return removed_count


# ==================== 命令行入口 ====================

def build_parser() -> argparse.ArgumentParser:
    """
    构建命令行参数解析器。

    返回:
        配置好的 ArgumentParser 对象
    """
    parser = argparse.ArgumentParser(
        description="本地文件管理工具：统计 / 重命名图片 / 大文件报告 / 清理空文件夹",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python file_manager.py -p ./my_folder --scan
  python file_manager.py -p D:\\Photos --rename-images
  python file_manager.py -p ./data --large-files --threshold 10
  python file_manager.py -p ./temp --clean-empty
  python file_manager.py -p ./work --all
        """,
    )

    parser.add_argument(
        "-p", "--path",
        required=True,
        help="要处理的文件夹路径（必填）",
    )

    # 功能开关（可多选）
    parser.add_argument(
        "--scan",
        action="store_true",
        help="统计文件总数及各类后缀数量",
    )
    parser.add_argument(
        "--rename-images",
        action="store_true",
        help="批量重命名图片为 image_001、image_002 ...",
    )
    parser.add_argument(
        "--large-files",
        action="store_true",
        help="筛选大文件并输出 report.txt",
    )
    parser.add_argument(
        "--clean-empty",
        action="store_true",
        help="递归删除空文件夹",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="依次执行全部功能",
    )

    # 可选参数
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_SIZE_THRESHOLD_MB,
        help=f"大文件阈值（MB），默认 {DEFAULT_SIZE_THRESHOLD_MB}",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="report.txt",
        help="大文件报告输出文件名，默认 report.txt",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：重命名/删空文件夹时不实际执行",
    )

    return parser


def main() -> None:
    """程序主入口：解析参数并调度各功能模块。"""
    parser = build_parser()
    args = parser.parse_args()

    try:
        root = validate_directory(args.path)
    except ValueError as exc:
        print(f"错误: {exc}")
        sys.exit(1)

    print(f"\n目标目录: {root.resolve()}\n")

    # 若未指定任何功能，默认只执行统计
    run_all = args.all
    do_scan = run_all or args.scan or not any([
        args.scan, args.rename_images, args.large_files, args.clean_empty, args.all
    ])
    do_rename = run_all or args.rename_images
    do_large = run_all or args.large_files
    do_clean = run_all or args.clean_empty

    if do_scan:
        stats = scan_directory_stats(root)
        print_scan_report(stats)

    if do_rename:
        rename_images_sequentially(root, dry_run=args.dry_run)

    if do_large:
        report_path = root / args.report
        find_large_files(root, threshold_mb=args.threshold, report_path=report_path)

    if do_clean:
        remove_empty_directories(root, dry_run=args.dry_run)

    print("全部任务执行完毕。")


if __name__ == "__main__":
    main()