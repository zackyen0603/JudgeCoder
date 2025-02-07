import os
import json

from .generators.openaiGenerator import OpenAIGenerator

class LLMGenerator:
    """
    Responsible for accepting prompt input and outputting the result using a large language model.
    """
    def __init__(self, model, api_key, data_dict):
        self.model = model
        self.api_key = api_key
        self.data_dict = data_dict

    
    # def save_to_temp_file(self, content, filename="temp.txt"):
    #     # Ensure the directory exists
    #     os.makedirs(os.path.dirname(filename), exist_ok=True)
    #     with open(filename, 'w', encoding='utf-8') as temp_file:
    #         temp_file.write(content)


    def _read_prompt_file(self, filename):
        """
        Read the content of a prompt file.
        """
        file_path = os.path.join(os.path.dirname(__file__), './prompts', filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


    def save2Json(self, input_dict, output_filename='output.json'):
        """
        Save the input dictionary to a JSON file. If the file exists, append to it.
        """
        output_path = os.path.join(os.path.dirname(__file__), output_filename)
        
        # Read existing data if the file exists
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                    if not isinstance(data, list):
                        data = [data]
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        # Append new data
        data.append(input_dict)

        # Write updated data back to the file
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Output .json file saved to {output_path}")




    def generate(self, question, prompt_file):
        """
        Generate output based on a provided prompt.
        """
        additional_prompt = self._read_prompt_file(prompt_file)
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




