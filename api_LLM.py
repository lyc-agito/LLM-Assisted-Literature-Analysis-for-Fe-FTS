import os, time, tiktoken
from transformers import AutoTokenizer
from openai import OpenAI


class cost_estimator:
    """估算一段 LLM 对话的价格"""

    def __init__(
            self,
            LLMs_cost=None,
            style='GPT'    # 默认模型风格
        ):
        """初始化信息：模型价格"""

        if LLMs_cost is None:
            self.LLMs_cost = {
                "qwen-max": {"input": 0.0024 / 1000, "output": 0.0096 / 1000},
                "qwen-max-0125": {"input": 0.0024 / 1000, "output": 0.0096 / 1000},
                "qwen-plus": {"input": 0.0008 / 1000, "output": 0.002 / 1000},
                "qwen-turbo": {"input": 0.0003 / 1000, "output": 0.0006 / 1000},
                "deepseek-v3": {"input": 0.002 / 1000, "output": 0.008 / 1000},
                "deepseek-r1": {"input": 0.004 / 1000, "output": 0.016 / 1000}
            }

        self.style = style
        
        self.cost_all = 0    # 初始化总价格

    def check_model(self, model_name):
        """检查模型的计费方式是否被录入"""

        if model_name not in self.LLMs_cost:
            print(f"\nWARNING！{model_name}的计费方式未被录入，改用Qwen-Max的计费方式进行计算。\n")
            model_name = 'qwen-max'

        return model_name

    @staticmethod
    def GPT_token_counter(
        analyzed_text,
        model_name='gpt-4'    # 默认模型名称：选择最常用的 GPT-4
        ):
        """按照 GPT 系列模型的分词方法计算文本的 token 数"""

        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(analyzed_text)
        
        return len(tokens)
    
    @staticmethod
    def Qwen_token_counter(
        analyzed_text,
        local_path="your_path"    # 设置本地Qwen分词器路径
        ):
        """按照 Qwen 系列模型的分词方法计算文本的 token 数"""

        tokenizer = AutoTokenizer.from_pretrained(local_path)
        tokens = tokenizer.tokenize(analyzed_text)

        return len(tokens)

    def cost_from_history(
            self,
            history,
            model_name='qwen-max'    # 默认计算模型：选择成本较高的 Qwen-Max
        ):
        """估算一段 LLM 对话（历史记录）的价格"""

        model_name = self.check_model(model_name)

        if self.style == 'GPT':
            
            for message in history:

                tokens = cost_estimator.GPT_token_counter(message['content'])

                if message['role'] == 'user' or message['role'] == 'system':                  
                    self.cost_all += tokens * self.LLMs_cost[model_name]['input']
                elif message['role'] == 'assistant':
                    self.cost_all += tokens * self.LLMs_cost[model_name]['output']
        
        elif self.style == 'Qwen':
            
            for message in history:

                tokens = cost_estimator.Qwen_token_counter(message['content'])

                if message['role'] == 'user' or message['role'] == 'system':                   
                    self.cost_all += tokens * self.LLMs_cost[model_name]['input']
                elif message['role'] == 'assistant':
                    self.cost_all += tokens * self.LLMs_cost[model_name]['output']

        else:
            print(f"警告！没有关于{self.style}的分词方法！")
    

class chain_API:
    """调用单个 LLM 的 API 用于单轮对话或多轮对话"""

    def __init__(
            self,
            model_name='qwen-turbo',    # 默认模型名称：选择成本较低的 Qwen-Max
            system_guidance="You are a helpful assistant.",    # 默认系统提示
            seed=20020506,    # 默认种子
            temperature=0    # 默认温度：选择确定性最强的 T=0
        ):
        """初始化信息：模型名称、系统提示、模型种子、模型温度、历史记录、对话成本"""

        self.model_name = model_name
        self.system_guidance = system_guidance
        self.seed = seed
        self.temperature = temperature

        self.history = [{"role": "system", "content": self.system_guidance}]    # 初始化历史记录
        self.time_consume_olist = []

        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),    # 可以换用其他平台的环境变量
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"    # 可以换用其它平台的URL
        )

        self.analyzed_text = None
        self.answer = None

        self.chain_cost = 0    # 初始化对话成本

    def API_analysis(
            self,
            analyzed_text="Tell me who you are in just one sentence.",    # 默认提示词：让模型做简单的自我介绍
            json_output=False    # 默认输出格式：不限制输出为 JSON 格式
        ):
        """按照提示词进行分析，更新分析时间和分析结果（可以选择限制为 JSON 格式）"""

        self.analyzed_text = analyzed_text
        self.history.append({"role": "user", "content": self.analyzed_text})    # 将提问更新至历史记录

        startTime = time.time()  # 计时开始

        if json_output:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history,
                seed=self.seed,
                temperature=self.temperature,
                response_format={"type": "json_object"}    # 限制输出为 JSON 格式
            )
        else:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history,
                seed=self.seed,
                temperature=self.temperature
            )

        time_consume = time.time() - startTime
        self.time_consume_olist.append(time_consume)

        self.answer = completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": self.answer})    # 将回答更新至历史记录

    def API_print(
            self,
            system_print=False,
            question_print=False,
            answer_print=True,
            time_consume_print=True,
            last_print=True    # 默认只打印最后一轮对话的内容
        ):
        """打印提示词、分析结果、分析时间"""

        if system_print:
            print(f"本次对系统设定为：\n{self.system_guidance}\n")

        if last_print:

            if question_print:
                print(f"我的问题是：\n{self.analyzed_text}\n")

            if answer_print:
                print(f"{self.model_name}的回答是：\n{self.answer}\n")

            if time_consume_print: 
                print(f"本次分析的耗时为：{self.time_consume_olist[-1]:.2f} s\n")

        else:

            for i in range(len(self.history)):

                if self.history[i]['role'] == 'user':
                    if question_print:
                        print(f"我的第{int((i + 1) / 2)}个问题是：\n{self.history[i]['content']}\n")
                elif self.history[i]['role'] == 'assistant':
                    if answer_print:
                        print(f"{self.model_name}对第{int(i / 2)}个问题的回答是：\n{self.history[i]['content']}\n")
                
            if time_consume_print:
                time_consume_list = [round(i, 2) for i in self.time_consume_olist]
                time_consume_all = round(sum(self.time_consume_olist), 2)
                print(f'本轮分析的耗时列表为：{time_consume_list}，总耗时为{time_consume_all} s\n')

    def API_cost(
            self,
            style='GPT'
        ):
        """估算当前 LLM 对话的价格"""

        i_cost = cost_estimator(style=style)
        i_cost.cost_from_history(self.history, model_name=self.model_name)
        self.chain_cost += i_cost.cost_all
