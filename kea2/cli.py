# coding: utf-8
# cli.py

from __future__ import absolute_import, print_function
import sys
from .utils import getProjectRoot, getLogger
from .kea_launcher import run
import argparse

import os
from pathlib import Path

from importlib.metadata import version
import json


logger = getLogger(__name__)


def cmd_version(args):
    print(version("Kea2-python"), flush=True)


def cmd_init(args):
    cwd = Path(os.getcwd())
    configs_dir = cwd / "configs"
    if os.path.isdir(configs_dir):
        logger.warning("Kea2 project already initialized")
        return

    import shutil
    def copy_configs():
        src = Path(__file__).parent / "assets" / "fastbot_configs"
        dst = configs_dir
        shutil.copytree(src, dst)

    def copy_samples():
        src = Path(__file__).parent / "assets" / "quicktest.py"
        dst = cwd / "quicktest.py"
        shutil.copyfile(src, dst)

    copy_configs()
    copy_samples()
    logger.info("Kea2 project initialized.")


def cmd_load_configs(args):
    pass


def cmd_report(args):
    from .bug_report_generator import BugReportGenerator
    try:
        report_dir = args.path
        if not report_dir:
            logger.error("Report directory path is required. Use -p to specify the path.")
            return

        if Path(report_dir).is_absolute():
            report_path = Path(report_dir)
        else:
            report_path = Path.cwd() / report_dir

        report_path = report_path.resolve()

        if not report_path.exists():
            logger.error(f"Report directory does not exist: {report_path}")
            return
        
        logger.debug(f"Generating test report from directory: {report_dir}")

        generator = BugReportGenerator()
        report_file = generator.generate_report(report_path)
        
        if report_file:
            logger.debug(f"Test report generated successfully: {report_file}")
            print(f"Report saved to: {report_file}", flush=True)
        else:
            logger.error("Failed to generate test report")

    except Exception as e:
        logger.error(f"Error generating test report: {e}")


def cmd_merge(args):
    """Merge multiple test report directories and generate a combined report"""
    from .report_merger import TestReportMerger

    try:
        # Validate input paths
        if not args.paths or len(args.paths) < 2:
            logger.error("At least 2 test report paths are required for merging. Use -p to specify paths.")
            return

        # Validate that all paths exist
        for path in args.paths:
            path_obj = Path(path)
            if not path_obj.exists():
                logger.error(f"Test report path does not exist: {path}")
                return
            if not path_obj.is_dir():
                logger.error(f"Path is not a directory: {path}")
                return

        logger.debug(f"Merging {len(args.paths)} test report directories...")

        # Initialize merger
        merger = TestReportMerger()

        # Merge test reports
        merged_dir = merger.merge_reports(args.paths, args.output)

        # Print results
        print(f"✅ Test reports merged successfully!", flush=True)
        print(f"📁 Merged report directory: {merged_dir}", flush=True)
        print(f"📊 Merged report: {merged_dir}/merged_report.html", flush=True)

        # Get merge summary
        merge_summary = merger.get_merge_summary()
        print(f"📈 Merged {merge_summary.get('merged_directories', 0)} directories", flush=True)

    except Exception as e:
        logger.error(f"Error during merge operation: {e}")


def find_new_config_files(src_dir, dst_dir):
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    
    if not src_path.exists():
        return []
    
    src_files = {f.relative_to(src_path) for f in src_path.rglob('*') if f.is_file()}
    dst_files = {f.relative_to(dst_path) for f in dst_path.rglob('*') if f.is_file()} if dst_path.exists() else set()
    
    new_files = [str(file_rel) for file_rel in src_files if file_rel not in dst_files]
    
    return new_files

def create_verison_info(version_file, version):
    version_info = {
        "version": version
    }
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=2, ensure_ascii=False)

def is_config_update_required(args) :
    base_dir = getProjectRoot()
    configs_dir = base_dir / "configs"
    version_file = configs_dir / "version.json"
    
    config_change = "0.3.6"
    version_cur = version("Kea2-python")
    version_config = "0.3.6"
    if not version_file.exists():
        version_config = "0.3.6"
        create_verison_info(version_file, version_config)
    else:
        with open(version_file, 'r', encoding='utf-8') as f:
            version_info = json.load(f)
        version_config = (version_info.get("version") or "0.3.6")
    if version_cur != version_config and version_config < config_change:
        logger.error(
            f"Configuration update required!\n"
            f"Current Kea2 version: {version_cur}\n"
            f"Configs version: {version_config}\n"
            f"Configurations were updated in version {config_change}\n"
            f"Please update your configuration files."
        )
        src = Path(__file__).parent / "assets" / "fastbot_configs"
        new_files = find_new_config_files(src, configs_dir)
        if new_files:
            print("\n🆕 List of newly added files:")
            for i, file_path in enumerate(new_files, 1):
                print(f"   {i:2d}. {file_path}")
    else:
        print(f"The configuration file does not need to be updated.\n")
        
        


def cmd_run(args):
    base_dir = getProjectRoot()
    if base_dir is None:
        logger.error("kea2 project not initialized. Use `kea2 init`.")
        return
    is_config_update_required()
    run(args)


_commands = [
    dict(action=cmd_version, command="version", help="show version"),
    dict(
        action=cmd_init,
        command="init",
        help="init the Kea2 project in current directory",
    ),
    dict(
        action=cmd_report,
        command="report",
        help="generate test report from existing test results",
        flags=[
            dict(
                name=["report_dir"],
                args=["-p", "--path"],
                type=str,
                required=True,
                help="Path to the directory containing test results"
            )
        ]
    ),
    dict(
        action=cmd_merge,
        command="merge",
        help="merge multiple test report directories and generate a combined report",
        flags=[
            dict(
                name=["paths"],
                args=["-p", "--paths"],
                type=str,
                nargs='+',
                required=True,
                help="Paths to test report directories (res_* directories) to merge"
            ),
            dict(
                name=["output"],
                args=["-o", "--output"],
                type=str,
                required=False,
                help="Output directory for merged report (optional)"
            )
        ]
    ),
    dict(
        action=is_config_update_required,
        command="check-config",
        help="check if configuration files need to be updated"
    )
]


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-d", "--debug", action="store_true",
                        help="show detail log")

    subparser = parser.add_subparsers(dest='subparser')

    actions = {}
    for c in _commands:
        cmd_name = c['command']
        actions[cmd_name] = c['action']
        sp = subparser.add_parser(
            cmd_name,
            help=c.get('help'),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        for f in c.get('flags', []):
            args = f.get('args')
            if not args:
                args = ['-'*min(2, len(n)) + n for n in f['name']]
            kwargs = f.copy()
            kwargs.pop('name', None)
            kwargs.pop('args', None)
            sp.add_argument(*args, **kwargs)

    from .kea_launcher import _set_runner_parser
    _set_runner_parser(subparser)
    actions["run"] = cmd_run
    if sys.argv[1:] == ["run"]:
        sys.argv.append("-h")
    args = parser.parse_args()

    import logging
    logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug("args: %s", args)

    if args.subparser:
        actions[args.subparser](args)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
