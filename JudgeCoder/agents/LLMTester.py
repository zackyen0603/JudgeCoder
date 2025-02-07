from .LLMBaseGenerator import LLMGenerator
import traceback
import threading
import concurrent.futures
import re

class LLMTester:
    """
    Responsible for executing tests against the generated code.
    """
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.code = data_dict['code']
        self.test_data = data_dict['test_list']
        self.passed_results = []
        self.error_report = []
        self.passed = True
        self.timeout_seconds = 5  # 設置執行的超時限制
        
    # def exec_with_timeout(self, code, namespace, timeout):
    #     exec_thread = threading.Thread(target=exec, args=(code, namespace))
    #     exec_thread.start()
    #     exec_thread.join(timeout)
    #     if exec_thread.is_alive():
    #         raise TimeoutError("Code execution exceeded the time limit")
    def exec_with_timeout(self, code, namespace, timeout):
        # 用於捕獲異常的列表
        exception_holder = []

        def target():
            try:
                exec(code, namespace)
            except Exception as e:
                exception_holder.append(e)

        exec_thread = threading.Thread(target=target)
        exec_thread.start()
        exec_thread.join(timeout)
        if exec_thread.is_alive():
            raise TimeoutError("Code execution exceeded the time limit")
        if exception_holder:
            raise exception_holder[0]



    def run_tests(self):
        """
        Execute tests on the provided code using the provided test data.
        """
        print(f"\n===\nExecuting tests on code: \n{self.code} \n\n===\n\nwith test data:")
        #print test data line by line
        for test in self.test_data:
            print(test)
        print("\n===\n\n")
            
        # Prepare a namespace for exec to run the code
        namespace = {}
            
        try:
            self.exec_with_timeout(self.code, namespace, self.timeout_seconds)
        except TimeoutError as e:
            print(f"Error executing code: {e}")
            self.passed = False
            self.data_dict['passed'] = False
            self.data_dict['code_error'] = True
            self.data_dict['code_error_message'] = str(e)
            return
        except Exception as e:
            print(f"Error executing code: {e}")
            self.passed = False
            self.data_dict['passed'] = False
            self.data_dict['code_error'] = True
            self.data_dict['code_error_message'] = traceback.format_exc() + '\n' + str(e)
            return           
            
        
# --- 增加超時版本前 ---  
#         # Execute the code to define the function in the namespace
#         try:
#             exec(self.code, namespace)
#         except Exception as e:
#             print(f"Error executing code: {e}")
#             self.passed = False
#             self.data_dict['passed'] = False
#             self.data_dict['code_error'] = True
#             self.data_dict['code_error_message'] = traceback.format_exc() +'\n'+ str(e)
#             return
#  --- 增加超時版本前 ---  

        # # Run each test case
        # print("--- Actual running results: ---")
        # for test_case in self.test_data:
        #     try:
        #         exec(test_case, namespace)
        #         result = self.get_function_result(test_case, namespace)
        #         self.passed_results.append(test_case)
        #     except AssertionError as e:
        #         result = self.get_function_result(test_case, namespace)
        #         self.error_report.append({"test_case":test_case,"result":result})
        #         self.passed = False
        #     except Exception as e:
        #         result = self.get_function_result(test_case, namespace)
        #         self.error_report.append({"test_case":test_case,"execute_result":result})
        #         self.passed = False
#  --- 增加超時版本前 ---  

                
        # print("--- Actual running results: ---")
        # for test_case in self.test_data:
        #     try:
        #         exec_with_timeout(test_case, namespace, self.timeout_seconds)

        #         result = self.get_function_result(test_case, namespace)
        #         self.passed_results.append(test_case)
        #     except AssertionError as e:
        #         result = self.get_function_result(test_case, namespace)
        #         self.error_report.append({"test_case": test_case, "result": result})
        #         self.passed = False
        #     except TimeoutError as e:
        #         self.error_report.append({"test_case": test_case, "result": str(e)})
        #         self.passed = False
        #     except Exception as e:
        #         result = self.get_function_result(test_case, namespace)
        #         self.error_report.append({"test_case": test_case, "execute_result": result})
        #         self.passed = False
                
        print("--- Actual running results: ---")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_test_case = {executor.submit(self.run_test_case, test_case, namespace): test_case for test_case in self.test_data}
            for future in concurrent.futures.as_completed(future_to_test_case):
                test_case = future_to_test_case[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error running test case {test_case}: {e}")               
                
                
        
        self.data_dict['passed_list'] = self.passed_results
        
        if self.passed:
            self.data_dict['passed'] = True
        else:
            self.data_dict['error_list'] = self.error_report
            

    def get_passed_results(self):
        return self.passed_results
    
    def get_errors(self):
        return self.error_report
    
    def ifPassed(self):
        return self.passed
    
    def ifCodeError(self):
        return self.data_dict['code_error']
    
    def get_function_result(self, test_case , namespace ):
        # 正則表達式來匹配函數調用部分
        pattern = r"assert\s+([\w_]+\(.+?\))\s*=="
        # 使用 re.search 來查找匹配
        match = re.search(pattern, test_case)

        # 如果找到匹配，提取匹配的部分
        if match:
            function_call = match.group(1)
            try:
                result = eval(function_call, namespace)
                print('\t' + function_call + " : " + str(result))
                return str(result)
            except Exception as e:
                error_message = f"Error executing function call '{function_call}': {str(e)}"
                traceback_info = traceback.format_exc()
                full_error_message = f"{error_message}\n{traceback_info}"
                print(full_error_message)
                return full_error_message
        else:
            print("No match found")
            return "Error: No match found"
    
        
    def run_test_case(self, test_case, namespace):
        try:
            self.exec_with_timeout(test_case, namespace, self.timeout_seconds)

            result = self.get_function_result(test_case, namespace)
            self.passed_results.append(test_case)
        except AssertionError as e:
            result = self.get_function_result(test_case, namespace)
            self.error_report.append({"test_case": test_case, "result": result})
            self.passed = False
        except TimeoutError as e:
            self.error_report.append({"test_case": test_case, "result": str(e)})
            self.passed = False
        except Exception as e:
            result = self.get_function_result(test_case, namespace)
            self.error_report.append({"test_case": test_case, "execute_result": result})
            self.passed = False
        

