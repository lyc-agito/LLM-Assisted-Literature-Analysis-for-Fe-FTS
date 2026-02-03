import os, sys, time, zipfile, re, requests
from io import BytesIO
from file_processer import find_txts, data_to_json


class MinerU_API:
    """用于调用 MinerU 的 API 批量处理 pdf 文件"""

    def __init__(
            self, 
            url="https://mineru.net/api/v4/file-urls/batch", 
            header=None
        ):
        """初始化信息：API URL、API KEY"""

        self.url = url
        if header is None:
            self.header = {
                "Content-Type": "application/json",
                "Authorization": "your_api"    ##### 设置API
            }
        
        self.pdf_folder_path = None
        self.pdf_file_paths = None
        self.pdf_file_names = None

        self.batch_id = None
        self.download_folder_path = None

        self.ready = True
        self.check = False

        self.log_json = []
    
    def get_pdf(
            self,
            pdf_folder_path
        ):
        """获取文件夹下的所有 pdf 文件的信息"""

        self.pdf_folder_path = pdf_folder_path

        self.pdf_file_paths = find_txts(self.pdf_folder_path, extension='.pdf')
        self.pdf_file_names = [os.path.basename(pdf_file_path) for pdf_file_path in self.pdf_file_paths]

        if len(self.pdf_file_paths) != len(self.pdf_file_names):
            self.ready = False
            print("文件名数量与文件路径数量不一致！")
    
    def process_pdf(
            self,
            ocr=False
        ):
        """调用 MinerU 的 API 处理 pdf 文件"""
        
        print(f"\n在{self.pdf_folder_path}中共有{len(self.pdf_file_paths)}个待处理的pdf文件。\n")

        condition = input('输入yes开始分析：')
        if condition != 'yes' or not self.ready:
            sys.exit()

        data = {
            "enable_formula": True,
            "enable_table": True,
            "language": "ch",
            "layout_model":"doclayout_yolo",
            "files": [
                {"name": pdf_file_name, "is_ocr": ocr, "data_id": "abcd"} for pdf_file_name in self.pdf_file_names
            ]
        }

        check_condition = True

        while check_condition:

            response = requests.post(self.url, headers=self.header, json=data)

            if response.status_code == 200:

                result = response.json()
                print(f"\n请求响应成功！\n")

                if result["code"] == 0:

                    batch_id = result["data"]["batch_id"]
                    self.batch_id = batch_id
                    print(f"本次解析的batch_id为：{batch_id}\n")

                    file_urls = result["data"]["file_urls"]

                    if len(file_urls) != len(self.pdf_file_paths):
                        print("URL数量与文件路径数量不一致！")
                        break

                    for index, file_url in enumerate(result["data"]["file_urls"]):
                            
                        with open(self.pdf_file_paths[index], 'rb') as f:
                            res_upload = requests.put(file_url, data=f)

                        if res_upload.status_code == 200:
                            print(f"文件{self.pdf_file_names[index]}已被成功上载！")
                        else:
                            print(f"文件{self.pdf_file_names[index]}上载失败！")
                    
                    check_condition = False

                else:
                    print(f"启用URL上载失败！报错信息为：{result.msg}")

            else:

                print(f"请求未响应成功，5秒后重新发送请求！当前状态为：{response.status_code}，响应结果为：\n{response}")

                time.sleep(5)

    def download_result(
            self,
            download_folder_path="your_path"    #### 设置md文件保存路径
        ):
        """下载解析结果"""

        self.download_folder_path = download_folder_path
        if not os.path.exists(self.download_folder_path):
            os.makedirs(self.download_folder_path)

        if self.batch_id is None:
            print("pdf文件尚未被提交处理！")

        elif self.check:
            
            url_for_download = f"https://mineru.net/api/v4/extract-results/batch/{self.batch_id}"

            res = requests.get(url_for_download, headers=self.header)

            for infos in res.json()['data']['extract_result']:

                if infos['err_msg']:
                    print(f"文件{infos['file_name']}解析失败！报错信息为：{infos['err_msg']}")
                else:
                    download_file_path = self.download_folder_path + '\\' + re.sub(r'\.', '', infos["file_name"])
                    file_url = infos["full_zip_url"]

                    res_download = requests.get(file_url)

                    if res_download.status_code == 200:

                        with zipfile.ZipFile(BytesIO(res_download.content)) as zip_ref:
                            zip_ref.extractall(download_file_path)
        
                        print(f"{infos['file_name']}的相关文件已下载并解压到：{download_file_path}")

        else:
            print("解析尚未完成！")
    
    def check_processing(
            self,
            manual_res_check=False,
            manual_states_check=False
        ):
        """检查 pdf 文件的解析进度"""

        if self.batch_id is None:
            print("pdf文件尚未被提交处理！")
            sys.exit()
        else:
            
            url_for_download = f"https://mineru.net/api/v4/extract-results/batch/{self.batch_id}"

            res = requests.get(url_for_download, headers=self.header)
            if manual_res_check:
                print(res.json())   ### 人工校验进度

            states= []
            for infos in res.json()['data']['extract_result']:
                states.append(infos['state'])
            if manual_states_check:
                print(states)
            if all(state in {'done', 'failed'} for state in states):
                print("解析已完成！")
                self.check = True
    
    @staticmethod
    def extract_md(
            md_name,
            md_lines,
            output_file_path,
            reference_delete=True
        ):
        """
        从 md 文件进行处理：如果可以匹配到 reference(s) 行，则删除其后的所有内容；如果匹配不到，则删除最后一个标题行后的内容
        """

        output = {"index": md_name, "process": None, "truncated_proportion": None}

        title_lines = [(i, title_line) for i, title_line in enumerate(md_lines) if re.match(r'^#+\s', title_line)]

        if not reference_delete:

            print("文本未经过任何处理！")
            output["process"], output["truncated_proportion"] = "未进行处理", 0
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.writelines(md_lines)
        
        elif not title_lines:

            print("没有发现标题行！")
            output["process"], output["truncated_proportion"] = "未发现标题行", 0
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.writelines(md_lines)
        
        else:

            reference_index = None

            for i, title_line in title_lines:

                if 'reference' in title_line.lower():
                    reference_index = i
                    print("存在Reference(s)标题行！删除其后的所有无关文本！")
                    output["process"] = "找到Reference(s)标题行"
                    break

            if reference_index is None:

                for i, line in enumerate(md_lines):

                    pure_line = line.strip()
                    if pure_line.lower() == 'reference' or pure_line.lower() == 'references':
                        reference_index = i
                        print("存在未被识别为标题行的Reference(s)！删除其后的所有无关文本！")
                        output["process"] = "找到未被识别的Reference(s)标题行"

            if reference_index is None:
                reference_index = title_lines[-1][0]
                print("不存在Reference(s)标题行！删除最后一个标题行后的所有无关文本！")
                output["process"] = "仅找到最后一个标题行"

            truncated_lines = md_lines[:reference_index]
            truncated_proportion = 100 - 100 * reference_index / len(md_lines)
            output["truncated_proportion"] = truncated_proportion

            if truncated_proportion > 60:
                print(f"警告！共计删除了约{truncated_proportion:.2f}%的无关文本！")
            else:
                print(f"共计删除了约{truncated_proportion:.2f}%的无关文本！")

            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.writelines(truncated_lines)

        print(f"处理结束！处理后的文件保存在{output_file_path}！\n")

        return output

    def get_txt(
            self,
            txt_target_folder="your_path",    ##### 设置txt文件保存路径
            reference_delete=True
        ):
        """
        将 MinerU 导出的系列文件夹中的 full.md 转化为文本，经过处理后保存
        """

        if not os.path.exists(txt_target_folder):
            os.makedirs(txt_target_folder)

        if self.download_folder_path is None:
            print("解析结果尚未被下载！")
            sys.exit()

        else:

            for root, dirs, files in os.walk(self.download_folder_path):

                for dir_name in dirs:

                    md_file_path = os.path.join(root, dir_name, 'full.md')

                    if os.path.exists(md_file_path):

                        txt_name = re.sub(r'\D', '', dir_name)    # 根据文件名的特点进行设置

                        txt_file_name = f"{txt_name}.txt"

                        print(txt_file_name)

                        txt_file_path = os.path.join(txt_target_folder, txt_file_name)

                        with open(md_file_path, 'r', encoding='utf-8') as md_file:
                            content = md_file.readlines()

                        self.log_json.append(
                            MinerU_API.extract_md(txt_name, content, txt_file_path, reference_delete=reference_delete)
                        )

    def write_log(
            self,
            log_path="your_path"    ###### 设置日志保存路径
    ):
        """将处理日志写入 json 文件"""

        data_to_json(log_path, self.log_json)
