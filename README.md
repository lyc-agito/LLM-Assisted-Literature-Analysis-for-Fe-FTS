# LLM-Assisted Literature Analysis for Fe FTS
提供“LLM-guided design of a high-loading iron carbide catalyst for efficient Fischer-Tropsch synthesis”一文中使用到的`python`代码（自2026年2月2日后不再更新）

`python` codes for "LLM-guided design of a high-loading iron carbide catalyst for efficient Fischer-Tropsch synthesis" (no more update after 2nd, February, 2025)
***
## file_processor.py
- `file_processor.py`定义了函数`data_to_json`和`find_txts`，用于实现基本的文件读写等操作；
- 使用时，应将`file_processor.py`文件放置于python的项目文件夹中，以方便对其进行导入。
- `file_processor.py` defines functions such as `data_to_json` and `find_txts` to handle basic file operations like reading and writing.
- One should place the `file_processor.py` file within the Python project directory for direct import.
## api_MinerU.py
- `api_MinerU.py`定义了定义了类`MinerU_API`，通过调用MinerU的API将pdf文件转化为md文件和txt文件。
- 使用时，应将`api_MinerU.py`文件放置于python的项目文件夹中，以方便对其进行导入。
- `api_LLM.py` defines the `MinerU_API` class, which interfaces with the API of MinerU to convert pdf documents into md documents and txt documnets.
- One should place the `api_LLM.py` file within the Python project directory for direct import.
## api_LLM.py
- `api_LLM.py`定义了类`class_API`，通过调用阿里云旗下大语言模型的API获取有关文献分析的信息，还定义了类`cost_estimator`，用于估算大语言模型分析的成本。
- 使用时，应将`api_LLM.py`文件放置于python的项目文件夹中，以方便对其进行导入。
- `api_LLM.py` defines the `class_API` class, which interfaces with the API of LLMs from Alibaba Cloud to retrieve information for literature analysis. It also defines the `cost_estimator` class for the estimation of LLM conversation cost.
- One should place the `api_LLM.py` file within the Python project directory for direct import.
## pdf2txt.py
- `pdf2txt.py`借助`api_MinerU`将pdf文件中的文本转化为markdown格式并将其写入txt文件中，方便后续直接输入给大语言模型。
- `pdf2txt.py` utilizes `api_MinerU` to convert text from pdf documents into markdown format and writes it into txt documents, facilitating subsequent input to LLMs.
## API_example.py
- 通过导入`api_LLM.py`中的函数与类调用指定大语言模型的API，对文献进行分析，并将分析结果写入日志。
- These scripts import functions and classes from `api_LLM.py` to invoke the specified large language model's API for literature analysis and log the analysis results.
