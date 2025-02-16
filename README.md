# JudgeCoder

## Project Introduction

This project leverages Large Language Models (LLM) to generate, test, and validate source code. The system is divided into several modules, each responsible for a specific task in the workflow. 

Below is a summary of the main features and functionalities implemented in this project.

## Implemented Features

### 1. **LLMGenerator Class**
   - **Description**: The base class for content generation using large language models.
   - **Features**:
     - **`__init__`**: Initializes the generator with the model, API key, and data dictionary.
     - **`save_to_temp_file`**: Saves the content to a temporary file.
     - **`_read_prompt_file`**: Reads the content of the specified prompt file.
     - **`save2Json`**: Saves the input dictionary to a JSON file, appending if the file exists.
     - **`generate`**: Generates output based on the provided prompt and additional prompt files.

### 2. **LLMProgrammer Class**
   - **Description**: Inherits from `LLMGenerator`, responsible for generating source code based on specified requirements.
   - **Features**:
     - **`generate_code`**: Uses the language model to generate code.
     - **`regenerate`**: Regenerates code if the initial generation fails.
     - **`initialize_data_dict`**: Initializes the data dictionary with default values.

### 3. **LLMUnitTestDeveloper Class**
   - **Description**: Inherits from `LLMGenerator`, responsible for generating unit test data for the generated code.
   - **Features**:
     - **`generate_test_data`**: Generates test data based on the context of the code.

### 4. **LLMTester Class**
   - **Description**: Responsible for running tests on the generated code.
   - **Features**:
     - **`run_tests`**: Runs the code tests using the provided test data.
     - **`get_passed_results`**: Returns a list of passed test results.
     - **`get_errors`**: Returns a list of errors encountered during testing.
     - **`ifPassed`**: Checks if all tests have passed.
     - **`ifCodeError`**: Checks if there are any errors in the code execution.
     - **`get_function_result`**: Evaluates and returns the function call results in the test cases.

### 5. **LLMJudge Class**
   - **Description**: Inherits from `LLMGenerator`, responsible for judging the correctness of the solution.
   - **Features**:
     - **`find_targets_in_text`**: Finds and returns targets in the text based on patterns.
     - **`judgement`**: Judges the correctness of the solution using prompts and generated code.

### 6. **JudgeCoder Class**
   - **Description**: Coordinates the workflow of code generation, test data generation, running tests, and judging the code.
   - **Features**:
     - **`execute`**: Executes the entire workflow from code generation to testing and judging.
     - **`print_data_dict`**: Prints the data dictionary in a readable format.
     - **`save_data_dict_to_json`**: Saves the data dictionary to a JSON file.
     - **`find_most_frequent_letter`**: Finds the most frequent letter in a given text.

---


## UML Graph
![UML Graph](/JudgeCoder_UML.jpg)

## Workflow

1. **Generate Code**: The `LLMProgrammer` class generates initial source code based on the given prompt.
2. **Generate Test Data**: The `LLMUnitTestDeveloper` class generates relevant test cases for the generated code.
3. **Run Tests**: The `LLMTester` class runs tests on the generated code, identifying any errors.
4. **Judge Code**: If tests fail, the `LLMJudge` class evaluates the code and errors, providing feedback for regeneration or correction.
5. **Regenerate Code**: If necessary, the `LLMProgrammer` class regenerates the code based on feedback, repeating this process until all tests pass or the maximum retry limit is reached.

---

## Prerequisites
1. **Create a virtual environment**
```bash
conda create -n {codex} python=3.7
conda activate {codex}
# {name can be customized}
```
2. **Install the openai package**
```
pip install openai
```

---

## HumanEval Evaluation

To verify the improvement in code generation accuracy in this project, we use HumanEval for evaluation.

1. **Download the human-eval package in any directory**
    ``` bash
    git clone https://github.com/openai/human-eval
    pip install -e human-eval
    ```

2. **Navigate to the first level directory of human-eval**
    ``` bash
    cd human-eval/
    ```
3. **Go to the human_eval/ directory and find the execution.py file, then uncomment line 58** 
    ``` python
    # exec(check_program, exec_globals)
    ```
    - The 8th line of the data.py file in that directory controls the reading of the dataset. You can change the test data by modifying the file in human-eval/data/
        ```python 
        HUMAN_EVAL = os.path.join(ROOT, "..", "data", "X.jsonl")
        ```
    

4. **Download JudgeCoder to the directory**
    ``` bash
    git clone https://github.com/zackyen0603/JudgeCoder.git
    ```

5. **Go back to the upper level directory of human-eval/ and create a .py file with the following content:**   
    ```python
    from human_eval.data import write_jsonl, read_problems
    from JudgeCoder.judgeCoder import JudgeCoder

    def generate_one_completion(task_id,prompt):
        api_key = "YOUR_API_KEY"
        model = "OPENAI_MODEL" # Documentation: https://platform.openai.com/docs/models/overview

        coder = JudgeCoder(model, api_key)
        result = coder.execute(task_id, prompt)
        return result

    def generate_sample(task_id, prompt):
        completion = generate_one_completion(task_id, prompt)
        return dict(task_id=task_id, completion=completion)

    ```

6. **Run the file to get the `samples.jsonl` output file**

7. **In the human-eval/ directory, execute the command to get the `samples.jsonl_results.jsonl` file, which will detail the test status of each generated code, and the `Terminal` will print out the execution status and `pass@K` values**
    - Execute the command
        ``` bash
        evaluate_functional_correctness samples0.jsonl 
        ```
    - Example result  
        ``` bash
        Reading samples...
        1it [00:00, 461.52it/s]
        Running test suites...
        100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 39.62it/s]
        Writing results to ../samples0.jsonl_results.jsonl...
        100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 290.95it/s]
        {'pass@1': 1.0}
        ```
