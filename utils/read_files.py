import os

# 指定要扫描的文件后缀
file_suffix = ".md"


def read_files_in_directory(folder_path):
    list = []
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(file_suffix):
                file_path = os.path.join(root, file_name)

                # 执行文件操作，例如读取文件内容
                with open(file_path, 'r') as file:
                    file_content = file.read()

                list.append({"file_path": file_path,
                            "file_content": file_content})
    return list
