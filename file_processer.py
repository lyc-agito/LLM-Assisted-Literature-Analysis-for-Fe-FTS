import os, time, json


def data_to_json(fold_path, datas):
    """将符合 JSON 格式的数据写入 json 文件"""

    if not os.path.exists(fold_path):
        os.makedirs(fold_path)

    log_name = input("请输入json日志名：")
    time_str = str(time.strftime('%Y%m%d_%H%M%S', time.localtime()))
    file_path = fold_path + '\\' + f'{log_name}' + f"_LOG_{time_str}.json"

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(datas, f, indent=4, ensure_ascii=False)


def find_txts(directory_path, extension='.txt'):
    """获取文件夹下所有 txt 文件的路径（也可以指定为其它类型的文件）"""

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    file_infos = []

    for file_name in os.listdir(directory_path):

        file_path = os.path.join(directory_path, file_name)

        if os.path.isfile(file_path):
            if os.path.splitext(file_name)[1].lower() == extension:
                file_infos.append(file_path)

    return file_infos
