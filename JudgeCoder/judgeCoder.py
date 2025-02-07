from .agents.LLMProgrammer import LLMProgrammer
from .agents.LLMUnitTestDeveloper import LLMUnitTestDeveloper
from .agents.LLMTester import LLMTester
from .agents.LLMJudge import LLMJudge

import os
import json
import uuid
import datetime
from typing import Dict, List, Tuple

from collections import Counter
import concurrent.futures
import threading

class JudgeCoder:
    def __init__(self, model, api_key):
        self.model = model
        self.api_key = api_key
        self.lock = threading.Lock()
        self.data_dict = self._initialize_data_dict() 
        self.total_retries = 0  # 添加全局重試計數器
        self.max_total_retries = 3  # 設置最大重試次數
        self.curr_depth = 0 #執行的最大深度
        self.max_depth = 3 #執行的最大深度
        
        
    def execute(self, task_id, question):
        self.data_dict['prompt'] = question
        self.data_dict['task_id'] = task_id
        return self._execute()
        

    def _execute(self):
        question = self.data_dict['prompt']
        
        if self.curr_depth >= self.max_depth:
            print("Exceeded maximum depth. Generation failed.")
            self.data_dict['report_result'] = "Exceeded maximum depth."
            return self.data_dict['code']
        
        self.curr_depth += 1
        
        test_data_count = 10

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 創建平行任務
            #生成程式碼
            future_program = executor.submit(self.generate_code, question)
            #生成{test_data_count}筆測試資料
            future_tests = executor.submit(self.generate_test_data, question, test_data_count )
            # 獲取結果
            code_output = future_program.result()
            test_output = future_tests.result()

        """ 
        -----非平行作法START-----
        # #生成程式碼
        # programmer = LLMProgrammer(self.model, self.api_key, self.data_dict)
        # code = programmer.generate_code(question)
        # #生成測試資料
        # unitTestDeveloper = LLMUnitTestDeveloper(self.model, self.api_key, self.data_dict)
        # test_data = unitTestDeveloper.generate_test_data(question)
        -----非平行作法END ----- 
        """
        
        #執行測試
        tester = LLMTester(self.data_dict)
        tester.run_tests()

        if not tester.ifPassed():
            print("Go To handle_test_failures\n")
            self.handle_test_failures(tester)
        else:
            self.save_data_dict_to_json()
            print("All tests passed! End Generation\n")

        return self.data_dict['code']

    def handle_test_failures(self, tester):
            max_rounds = 3
            code_error_limit = 3
            current_round = 0
            
            #重複執行流程直到通過測試或超過指定次數
            while not tester.ifPassed() and current_round < max_rounds :
                print('========== Start a new round ===========\n')
                current_round += 1 


                #生成錯誤，需要重新生成程式碼（可能是未包含一些東西：函式名或import）
                errorTime = 0 #錯誤次數
                while tester.ifCodeError() and errorTime < code_error_limit :
                    errorTime += 1
                    print(f"Code error {errorTime} time:\n")
                    print('# NEED Programmer To Regenerate Code')
                    # parent_id , child_id = self.regenerate_code()
                    # self.update_child_id_in_json(parent_id, child_id)
                    self.generate_code(self.data_dict['prompt'])
                    
                    # tester = LLMTester(self.data_dict)
                    tester.run_tests()
                    
                    if tester.ifPassed():
                        print("All tests passed after regenerating code.")
                        return True
                    else:
                        print('重新生成還是不OK')
                        # self.save_data_dict_to_json()
                    

                print(f"========== The {current_round} time try ===========\n")
                print("Some tests failed:")
                for result in tester.get_errors():
                    print('\t',result)
                
                #交由{judge_num}位法官判斷多數決
                judge_num = 3
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(self.judge_code) for _ in range(judge_num)]
                    for future in concurrent.futures.as_completed(futures):
                        future.result()
                    
                most_voted_answer, voted_count = self.find_most_frequent_vote()

                """
                ## -----非平行作法START-----
                # for i in range(judge_num):
                #     print("\n---Judgement",i+1, "starting: ---\n")
                #     judge = LLMJudge(self.model, self.api_key, self.data_dict)
                #     judge.judgement()
                
                # most_voted_answer, count = self.find_most_frequent_letter(self.data_dict['vote'])
                ## -----非平行作法END -----
                """

                if most_voted_answer == 'A':
                    print('# programmer.regenerate()')
                    #先儲存資料，準備新增新的一筆資料
                    new_test_cases = self.regenerate_test_data()
                    parent_id , child_id = self.regenerate_code()
                    self.update_child_id_in_json(parent_id, child_id)
                    self.data_dict['test_list'] = new_test_cases
                    tester = LLMTester(self.data_dict)
                    tester.run_tests()


                elif most_voted_answer == 'B':
                    # 代表程式碼沒問題，但是測試資料有問題
                    # 直接輸出程式碼看看
                    self.data_dict['passed'] = True
                    self.save_data_dict_to_json()
                    return True
                
                elif most_voted_answer == 'C':
                    print("兩個都錯 重新生成資料")
                    self.total_retries += 1  # 更新重試計數器
                    return self._execute()
                
                else:
                    print("不可能會到這（たぶん），但還是整個重生一下")
                    self.total_retries += 1  # 更新重試計數器
                    return self._execute()
                


            if current_round >= max_rounds:
                print("Exceed the maximum number of retries.")
                self.data_dict['report_result'] = "Exceed the maximum number of retries."
                self.save_data_dict_to_json()
                #回傳最後一輪的程式碼(可能有錯誤)            
                return False
            else:             
                print("All tests passed!")
                return True


    # 印出data_dict資訊
    def print_data_dict(self):
        """
        Print the data_dict information in a readable format.
        """
        print(json.dumps(self.data_dict, indent=4))


    def save_data_dict_to_json(self, output_filename='output.json'):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data_dict["generated_time"] = current_time

        output_path = os.path.join(os.path.dirname(__file__), output_filename)

        with self.lock:
            try:
                # 確保文件存在，並處理文件初次創建的情況
                if not os.path.exists(output_path):
                    with open(output_path, 'w', encoding='utf-8') as file:
                        file.write("[]")

                # 以 'r+' 模式打開文件，允許讀寫操作，不刪除文件內容
                with open(output_path, 'r+', encoding='utf-8') as file:
                    file.seek(0, os.SEEK_END)               # 移動到文件末尾
                    position = file.tell() - 1              # 定位到最後一個字符
                    while position > 0:
                        file.seek(position)
                        if file.read(1) == "]":
                            file.seek(position)
                            break
                        position -= 1

                    if position > 1:                       # 檢查文件是否僅含空的 JSON 數組
                        file.write(',\n')                  # 在前一個元素後添加逗號和換行
                    else:
                        file.write('\n')

                    # 使用 json.dumps 美化格式化輸出，包括縮進
                    file.write(json.dumps(self.data_dict, ensure_ascii=False, indent=4))
                    file.write("\n]")  # 寫入新數據並重新結尾，並添加換行符
            except Exception as e:
                print(f"An error occurred: {e}")

        print(f"Data saved to {output_path}")








    def update_child_id_in_json(self, parent_id, child_id):
        """
        在 output.json 文件中找到 parent_id，並將 child_id 加入該記錄。
        """
        with self.lock:
            output_path = os.path.join(os.path.dirname(__file__), 'output.json')
            if os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        print("Error decoding JSON from output file.")
                        return

                # 更新 child_id 資訊
                updated = False
                for data in existing_data:
                    if data.get('judge_id') == parent_id:
                        data['child_id'] = child_id
                        updated = True
                        
                if updated:
                    with open(output_path, 'w', encoding='utf-8') as json_file:
                        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
                    print(f"Updated child_id in {output_path}")
            else:
                print(f"Parent ID {parent_id} not found in {output_path}")
                    
                    
    def find_most_frequent_vote(self):
        vote_counter = Counter(self.data_dict['vote'])
        if all(vote == 0 for vote in vote_counter.values()):
            return "A", 0  # 或者其他適合的處理方式，例如返回一個特殊值或錯誤訊息

        most_voted, count = vote_counter.most_common(1)[0]
        # 檢查是否存在票數相同的情況
        if list(vote_counter.values()).count(count) > 1:
            return "A", count  # 如果有多個最高票數相同，也可以返回特殊值或錯誤訊息

        return most_voted, count

    
    def generate_code(self, question):
        programmer = LLMProgrammer(self.model, self.api_key, self.data_dict)
        return programmer.generate_code(question)

    def generate_test_data(self, question, question_number=10 ):
        unitTestDeveloper = LLMUnitTestDeveloper(self.model, self.api_key, self.data_dict)
        return unitTestDeveloper.generate_test_data(question, question_number)
    
    def regenerate_test_data(self):
        unitTestDeveloper = LLMUnitTestDeveloper(self.model, self.api_key, self.data_dict)
        return unitTestDeveloper.regenerate_test_data()
    
    def regenerate_code(self):
        parent_id = self.save_data_dict_to_json()
        programmer = LLMProgrammer(self.model, self.api_key, self.data_dict)
        programmer.regenerate()
        return parent_id , self.data_dict['judge_id']
    
    def judge_code(self):
        judge = LLMJudge(self.model, self.api_key, self.data_dict)
        judge.judgement()
        
    def _initialize_data_dict(self) :
        return {
            "judge_id": str(uuid.uuid4()), #法官ID
            "parent_id": "", #父親ID
            "child_id": "",  #孩子ID
            "generated_time" : "", #生成時間

            "source_file": "",
            "task_id": "", #題目ID
            "prompt": "", #題目
            #---生成程式碼資料---
            "prompt_code_generation": "", #生成程式碼的prompt
            "response_code": "",          #生成的程式碼回應
            "code_error": False,          #生成程式碼是否有錯誤
            "code_error_message": "",     #生成程式碼錯誤訊息
            "code": "", #處理過的code
            #---生成測試資料---
            "prompt_test_generation": "", #生成測試資料的prompt
            "response_test_case": "",     #生成的測試資料回應
            "test_list": [],   #一筆一筆分割的測試資料
            "passed_list": [], #執行後通過的測試資料
            "error_list": {},  #執行後導致錯誤的測試資料
            #---判決相關資料---
            "prompt_judge_generate": "",        #判斷程式碼的prompt
            "response_judge": [],               #判斷的回應
            "vote": {"A": 0, "B": 0, "C": 0},   #法官投票

            "completion": "",
            "full_code": "",
            "report_passed": False,
            "report_result": "",
            "result": "",

            "passed": False,    #是否通過測試
            "api_cost": 0,      #API花費
            "process_time": 0,  #處理時間

        } #法官的紀錄書