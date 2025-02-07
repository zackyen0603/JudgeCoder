from .LLMBaseGenerator import LLMGenerator
from .generators.openaiGenerator import OpenAIGenerator

class LLMUnitTestDeveloper(LLMGenerator):
    """
    Responsible for generating test data for the generated code using a large language model.
    """



    def generate_test_data(self, question ,question_number=10):
        """
        Generate test data based on the context of the code.
        """
        prompt_file = "prompt_data_generate.txt"

        additional_prompt = self._read_prompt_file(prompt_file)
        # prompt = f"\n{additional_prompt}\n{question}\n"
        prompt = additional_prompt.format(question=question, question_number=str(question_number))

        self.data_dict['prompt_test_generation'] = prompt


        print('Generating tests... ',end='')
        output = self.generate(question, prompt)
        print('Tests generated.\n')

        # Parse the string output into a list of test cases
        test_output_str = output['output'].strip('```python').strip('```').strip()
        test_list = [line.strip() for line in test_output_str.split('\n') if line.strip() and line.strip().startswith("assert")]

        self.data_dict['response_test_case'] = output['output']
        self.data_dict['test_list'] = list(set(test_list))  # Ensure uniqueness by converting to a set and back to a list
        
        return output

    def regenerate_test_data(self):
        """
        Regenerate test data based on the number of errors in data_dict['error_list'].
        """
        error_count = len(self.data_dict['error_list'])
        if error_count == 0:
            print("No errors to regenerate test data for.")
            return
        
        
        prompt_file = "prompt_data_generate.txt"

        question = self.data_dict['prompt']
        additional_prompt = self._read_prompt_file(prompt_file)
        # prompt = f"\n{additional_prompt}\n{question}\n"
        prompt = additional_prompt.format(question=question, question_number=str(error_count))
        self.data_dict['prompt_test_generation'] = prompt
        

        print(f"Regenerating {error_count} new tests...")
        new_tests_output = self.generate(question, prompt)
        print('New tests generated.\n')

        # Parse the new test cases
        new_test_output_str = new_tests_output['output'].strip('```python').strip('```').strip()
        new_test_list = [line.strip() for line in new_test_output_str.split('\n') if line.strip() and line.strip().startswith("assert")]

        # Add new tests to the existing test list, ensuring uniqueness
        current_test_set = set(self.data_dict['passed_list'])
        new_test_set = set(new_test_list)
        combined_test_list = list(current_test_set.union(new_test_set))

        self.data_dict['test_list'] = combined_test_list
        self.data_dict['response_test_case'] += "\n" + new_tests_output['output']  # Append the new test cases to the response
        
        return combined_test_list


    def generate(self, question, prompt):
        """
        Generate output based on a provided prompt.
        """
        additional_prompt = prompt
        prompt = f"\n{additional_prompt}\n{question}\n"

        # print(f"=====\nGenerating output for prompt: \n{prompt}\n=====\n")

        generator = OpenAIGenerator(self.api_key)
        # generator.set_temperature(0.7)
        output = generator.generate(prompt)

        self.data_dict['api_cost'] += output.get('usage', 0)
        self.data_dict['process_time'] += output.get('process_time', 0)
        
        # self.save2Json(output, 'output.json')

        # print(output)
        
        return output