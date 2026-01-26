from . import dataparser
from . import analyzer
from . import analyzer
from . import analyzeplot
import argparse
import os
import subprocess
import concurrent.futures
import traceback
from tqdm import tqdm
from .config import CONF_OUTPUT_FOLDER, CONF_AUTO_SKIP_PARSE

MAX_WORKERS = 4


def main(data_input):
    if os.path.isfile(data_input) is False:
        print(f"Error: {data_input} does not exist.")
        return
    if data_input.endswith('.bin'):
        file_name = os.path.basename(data_input).replace('.bin', '')
    elif data_input.endswith('_data.json'):
        file_name = os.path.basename(data_input).replace('_data.json', '')
    elif data_input.endswith('_analyze.json'):
        file_name = os.path.basename(data_input).replace('_analyze.json', '')
    data_path = os.path.join(
        CONF_OUTPUT_FOLDER, file_name + '_data.json')
    analyze_path = os.path.join(
        CONF_OUTPUT_FOLDER, file_name + '_analyze.json')

    if data_input.endswith('.bin'):
        if CONF_AUTO_SKIP_PARSE and os.path.exists(data_path):
            # 对比修改日期 如果bin文件的修改日期比data文件的修改日期要新 则重新解析
            if os.path.getmtime(data_input) > os.path.getmtime(data_path):
                dataparser.parse_data_file(data_input, data_path)
            else:
                print(f"Skip {data_input} because {data_path} already exists.")
        else:
            dataparser.parse_data_file(data_input, data_path)
        analyzer.analyze_file(data_path, analyze_path)
        analyzeplot.analyze_plot(analyze_path)
    elif data_input.endswith('_data.json'):
        analyzer.analyze_file(data_input, analyze_path)
        analyzeplot.analyze_plot(analyze_path)
    elif data_input.endswith('_analyze.json'):
        analyzeplot.analyze_plot(data_input)

    return file_name


if __name__ == '__main__':
    if not os.path.exists(CONF_OUTPUT_FOLDER):
        os.makedirs(CONF_OUTPUT_FOLDER)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', help='Path to the binary file', required=False)
    parser.add_argument(
        '-p', '--path', help='Path to the binary folder', required=False
    )
    # auto skip
    parser.add_argument(
        '-s', '--skip', help='Skip the file if the output file already exists', action='store_true', required=False)
    args = parser.parse_args()

    # 如果没有命令行参数
    if not args.file and not args.path:
        args.path = 'D:\COMTOOL'
        args.skip = True

    if args.file:
        main(data_input=args.file)
        exit(0)
    if args.path:
        folder_path = args.path
        if not os.path.exists(folder_path):
            print(f"Error: {folder_path} does not exist.")
            exit(1)

        file_list = [file_name for file_name in os.listdir(
            folder_path) if file_name.endswith(".bin")]
        progress_bar = tqdm(total=len(file_list), desc="Processing files")

        def process_file(file_path, progress_bar):
            log_path = os.path.join(
                CONF_OUTPUT_FOLDER, os.path.splitext(os.path.basename(file_path))[0] + '.log')

            with open(log_path, 'w') as log_file:
                process = subprocess.Popen(['python', '-m', 'calibration_analyzer.main', '-f', file_path],
                                           stdout=log_file, stderr=subprocess.PIPE)
                process.wait()  # 等待子进程完成

            progress_bar.update(1)

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            files_to_process = []
            for file_name in file_list:
                file_path = os.path.join(folder_path, file_name)
                log_path = os.path.join(
                    CONF_OUTPUT_FOLDER, os.path.splitext(os.path.basename(file_path))[0] + '.log')
                analyze_path = os.path.join(
                    CONF_OUTPUT_FOLDER, os.path.splitext(os.path.basename(file_path))[0] + '_analyze.json')
                png_path = os.path.join(
                    CONF_OUTPUT_FOLDER, os.path.splitext(os.path.basename(analyze_path))[0] + '.png')
                if args.skip and os.path.exists(log_path) and os.path.exists(analyze_path) and os.path.exists(png_path):
                    # 对比修改日期 如果bin文件的修改日期比data文件的修改日期要新 则重新解析
                    if os.path.getmtime(file_path) > os.path.getmtime(log_path):
                        files_to_process.append(file_path)
                    else:
                        pass
                    progress_bar.update(1)
                    continue
                files_to_process.append(file_path)

            print(f"Found {files_to_process} files to process.")
            for file_path in files_to_process:
                futures.append(executor.submit(
                    process_file, file_path, progress_bar))

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    traceback.print_exc()

        progress_bar.close()
        exit(0)
