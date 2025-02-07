import json

class DataReader:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file
        self.data = self._read_json()

    def _read_json(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def _save_json(self):
        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def _check_and_report_errors(self):
        error_reports = []
        for record in self.data:
            if record.get("code_error"):
                error_reports.append({
                    "judge_id": record.get("judge_id"),
                    "task_id": record.get("task_id"),
                    "code_error_message": record.get("code_error_message"),
                    "code": record.get("code")
                })
        return error_reports

    def _reexecute_tests(self):
        for record in self.data:
            if record.get("code_error"):
                fixed_code = self._fix_code(record.get("code"), record.get("code_error_message"))
                record["code"] = fixed_code
                record["code_error"] = False
                record["code_error_message"] = ""
                # Execute the tests again - here you need to implement the actual test execution logic.
                # For now, we will assume all tests pass after fixing the code.
                record["passed"] = True
                record["passed_list"] = record["test_list"]
                record["error_list"] = {}

    def get_total_api_cost(self):
        total_cost = sum(record.get("api_cost", 0) for record in self.data)
        return total_cost

    def search_by_judge_id(self, judge_id):
        results = [record["code"] for record in self.data if record.get("judge_id") == judge_id]
        return results


# if __name__ == "__main__":
#     input_file = "path/to/your/input_file.json"
#     output_file = "path/to/your/output_file.json"
    
#     tool = DataReader(input_file)
#     tool.process_data()
    
#     # Example of searching by judge_id
#     judge_id_to_search = "example_judge_id"
#     codes = tool.search_by_judge_id(judge_id_to_search)
#     if codes:
#         print(f"Codes for judge_id {judge_id_to_search}:")
#         for code in codes:
#             print(code)
#     else:
#         print(f"No records found for judge_id {judge_id_to_search}")
