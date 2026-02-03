import time
from api_MinerU import MinerU_API


api = MinerU_API()
api.get_pdf("your_path")    ##### 设置pdf文件输入路径
api.process_pdf()

start_time = time.time()
condition = True
while condition:    # 轮询解析结果

    api.check_processing()
    
    if api.check:
        api.download_result("your_path")    ##### 设置md文件输出路径
        condition = False
    else:
        time_step = 10
        print(f"\n解析尚未完成！等待{time_step}秒后再次检查...\n")   
        time.sleep(time_step)
        if time.time() - start_time > time_step * len(api.pdf_file_paths):    
            print("解析超时！")
            condition = False

api.get_txt(txt_target_folder="your_path")    ##### 设置txt文件输出路径
api.write_log(log_path="your_path")    ##### 设置日志文件输出路径
