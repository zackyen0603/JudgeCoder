from .LLMBaseGenerator import LLMGenerator
from .generators.openaiGenerator import OpenAIGenerator

import re
import threading


class LLMJudge(LLMGenerator):
    """
    Responsible for judging the correctness of a solution using a large language model.
    """
    def __init__(self, model, api_key, data_dict):
        super().__init__(model, api_key,data_dict)
        self.lock = threading.Lock()  # 加鎖，防止多執行續操作時的資料競爭問題
        
    def find_targets_in_text(self, text):
        pattern = re.compile(r'\[\[(.*?)\]\]')
        return pattern.findall(text)
    

    def judgement(self):
        """
        Judge the correctness of a solution using a language model based on a provided prompt and code.
        """
        code = self.data_dict['code']
        error_cases = self.data_dict['error_list']

        prompt_file = "prompt_judge_generate.txt"
        prompt = self._read_prompt_file(prompt_file)

        question = self.data_dict['prompt']
        test_code = self.data_dict['code']
        test_passed_cases = "Passed cases:\n" + "\n".join(self.data_dict['passed_list'])
        # test_error_cases = "Error cases:\n" + "\n".join(self.data_dict['error_list'])
        test_error_cases = "Error cases:\n"
        # 遍歷 error_list，格式化每個條目的 test_case 和 execute_result
        for error in self.data_dict['error_list']:
            test_case = error.get('test_case', 'N/A')  # 獲取 test_case，默認為 'N/A'
            execute_result = error.get('result', 'N/A')  # 獲取 execute_result，默認為 'N/A'
            # 將格式化後的字符串添加到 error_cases
            test_error_cases += f"Test Case and Excepted answer: {test_case}, Actual Execute output: {execute_result}\n"

        prompt = prompt.format(
            question=question, 
            code=test_code, 
            error_cases=test_error_cases, 
            passed_cases=test_passed_cases
        )

        self.data_dict['prompt_judge_generate'] = prompt

        print('Judging... ',end='')
        # output = self.generate(code, "temp.txt")
        output = self.generate_from_prompt(prompt)
        print('Finished.\n')

        self.data_dict['response_judge'].append(output['output']) 


        print(f" ++ Judgement result: ++ \n{output['output']}")

        targets = self.find_targets_in_text(output['output'])
        if targets:
            res = targets[0].upper()
                
            with self.lock:  # 使用锁保护对投票字典的修改
                if res in self.data_dict['vote']:
                    self.data_dict['vote'][res] += 1
                else:
                    print("投票錯誤，請檢查程式碼是否有誤")
        else:
            print("No targets found in the output.")

        print("目前票匭狀況：",self.data_dict['vote'])
    
    def generate_from_prompt(self, prompt):
        """
        Generate output directly from a prompt string without using temporary files.
        """
        generator = OpenAIGenerator(self.api_key)
        # generator.set_temperature(0.7)
        output = generator.generate(prompt)
        
        self.data_dict['api_cost'] += output.get('usage', 0)
        self.data_dict['process_time'] += output.get('process_time', 0)
        
        return output