## 本地文件管理工具（file_manager.py）

一个基于 Python 标准库的本地文件夹管理脚本，支持文件统计、图片批量重命名、大文件扫描与空文件夹清理。无需安装第三方依赖。

### 功能介绍

| 功能 | 命令参数 | 说明 |
|------|----------|------|
| 文件统计 | `--scan` | 递归遍历指定目录，统计文件总数，并按类型分类计数（Python / Markdown / 文本 / HTML / 图片 / 文档 / 压缩包 / 音视频 / 其他） |
| 图片重命名 | `--rename-images` | 将目录内所有图片统一重命名为 `image_001`、`image_002` … 格式，保留原后缀 |
| 大文件报告 | `--large-files` | 筛选大于指定大小（默认 10 MB）的文件，生成清单并保存为 `report.txt` |
| 清理空文件夹 | `--clean-empty` | 自底向上递归删除空目录（不删除根目录本身） |
| 一键全功能 | `--all` | 依次执行以上全部功能 |

**支持的图片格式：** `.jpg`、`.jpeg`、`.png`、`.gif`、`.bmp`、`.webp`、`.tiff`、`.tif`、`.svg`、`.ico`

**默认行为：**

- 未指定任何功能参数时，默认只执行文件统计（`--scan`）
- 大文件报告默认输出到目标目录下的 `report.txt`

### 环境要求

- Python 3.10 及以上
- 仅使用 Python 标准库，无需 `pip install`

### 运行方法

#### 基本语法

```bash
python file_manager.py -p <文件夹路径> [功能参数] [可选参数]
```

#### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `-p`, `--path` | 是 | 要处理的文件夹路径（相对或绝对路径均可） |
| `--scan` | 否 | 统计文件数量 |
| `--rename-images` | 否 | 批量重命名图片 |
| `--large-files` | 否 | 生成大文件报告 |
| `--clean-empty` | 否 | 删除空文件夹 |
| `--all` | 否 | 执行全部功能 |
| `--threshold` | 否 | 大文件阈值（MB），默认 `10` |
| `--report` | 否 | 报告文件名，默认 `report.txt` |
| `--dry-run` | 否 | 预览模式，重命名/删空文件夹时不实际执行 |

#### 使用示例

```powershell
# 进入脚本所在目录
cd E:\CuisorCK\2026

# 统计文件（默认行为，可省略 --scan）
python file_manager.py -p .\test
python file_manager.py -p .\test --scan

# 预览图片重命名（推荐先预览）
python file_manager.py -p .\test --rename-images --dry-run

# 正式重命名图片
python file_manager.py -p .\test --rename-images

# 扫描大于 10 MB 的大文件
python file_manager.py -p .\test --large-files

# 自定义阈值 20 MB，报告保存为 big_files.txt
python file_manager.py -p .\test --large-files --threshold 20 --report big_files.txt

# 预览并删除空文件夹
python file_manager.py -p .\test --clean-empty --dry-run
python file_manager.py -p .\test --clean-empty

# 一次性执行全部功能
python file_manager.py -p .\test --all

# 组合多个功能
python file_manager.py -p .\test --scan --large-files
```

#### 路径写法

```powershell
# 相对路径
python file_manager.py -p .\photos

# 绝对路径
python file_manager.py -p E:\CuisorCK\2026\test

# 路径含空格时需加引号
python file_manager.py -p "D:\My Photos"
```

#### 查看帮助

```bash
python file_manager.py -h
```

### 输出说明

**文件统计（控制台）**

输出文件总数，以及 Python、Markdown、图片等各类型的数量。

**大文件报告（report.txt）**

报告包含：扫描目录、扫描时间、阈值、大文件数量，以及每个大文件的序号、大小、相对路径。

### 注意事项

1. 请在测试目录中验证后再对重要资料目录执行写操作。
2. `--rename-images` 和 `--clean-empty` 会修改文件系统，建议先用 `--dry-run` 预览结果。
3. 图片重命名采用两阶段策略避免文件名冲突，但操作完成后无法通过脚本还原，请提前备份重要图片。
4. `--clean-empty` 只删除子目录中的空文件夹，传入的根目录本身不会被删除。
5. 大文件报告默认保存在被扫描目录内（如 `test/report.txt`），可通过 `--report` 自定义文件名。
6. 若目录或文件被占用、无读写权限，部分操作可能跳过并在控制台提示，不会中断整个程序。
7. 所有功能均会递归处理子目录，请确认 `-p` 指向的目录范围是否符合预期。
8. 使用 `--all` 或多参数组合时，执行顺序为：统计 → 重命名图片 → 大文件报告 → 清理空文件夹。