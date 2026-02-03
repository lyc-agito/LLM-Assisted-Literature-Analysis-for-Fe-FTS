import sys, time
from pathlib import Path
from file_processer import find_txts, data_to_json
from api_LLM import chain_API


prompt_opt = 'your_prompt'    ##### 设置提示词

txt_fold = "your_path"    ##### 设置txt文件输入路径
sleep_time = 0    ##### 设置延迟时间

files = find_txts(txt_fold)
print(f'\n{txt_fold}中共有{len(files)}个txt文件。\n')
# files = files[:5]    ##### 调节分析范围（用于测试）

condition = input('输入yes开始分析：')
if condition != 'yes':
    sys.exit()

answers = []
total_cost, processing_time, processing_times = 0, 0, 0

for file in files:

    filePath = Path(file)
    index = filePath.stem
    print(index)

    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    api = chain_API(
        model_name='your_model',    ### 设置模型类型
        system_guidance='You are a helpful assistant.',    ### 设置提示语
    )
    api.API_analysis(analyzed_text=prompt_opt + f'<attachment>\n{text}\n</attachment>')
    api.API_print()

    api.API_cost(style='Qwen')
    total_cost += api.chain_cost

    processing_time += api.time_consume_olist[-1]
    processing_times += 1

    answer_dict = {
        "index": index,
        "answer": api.answer,
        "cost": api.chain_cost,
        "time_consume": api.time_consume_olist[-1]
    }
    answers.append(answer_dict)

    time.sleep(sleep_time)

log_date = input("请输入日志文件夹：")
output_path = "your_path"    ##### 设置日志文件输出路径
log_fold_path = output_path + '\\' + log_date

data_to_json(log_fold_path, answers)

print(
    f"运行结束！\n本次共分分析了{processing_times}篇文章，耗时{processing_time / 60:.2f}分钟，"
    f"延迟耗时{sleep_time * processing_times / 60:.2f}分钟。\n估算总耗费{total_cost:.2f}元。"
)
