import json
import sys
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import radiolist_dialog, button_dialog
from prompt_toolkit.styles import Style

def load_data(file_path):
    """Load the data from a .jsonl file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
        return data
    except Exception as e:
        return str(e)


def list_failed_tasks(data):
    """List the tasks where 'passed' is False, along with their 'task_id' and the function name from 'completion'."""
    failed_tasks = []
    for entry in data:
        if not entry['passed']:
            function_name = entry['completion'].split('def ')[1].split('(')[0].strip() if 'def ' in entry['completion'] else "Unknown Function"
            inputs = entry['completion'].split('(')[1].split(')')[0].strip() if '(' in entry['completion'] and ')' in entry['completion'] else "No inputs"
            failed_tasks.append({'task_id': entry['task_id'], 'function_name': function_name, 'inputs': inputs})
    return failed_tasks

def calculate_pass_rate(data):
    """Calculate and return the pass rate for the dataset."""
    total = len(data)
    passed = sum(1 for entry in data if entry['passed'])
    pass_rate = (passed / total) * 100 if total > 0 else 0
    return pass_rate

def find_task_by_id(data):    
    """Allows user to interactively select a task and view its completion."""
    task_ids = [entry['task_id'] for entry in data]
    task_completer = WordCompleter(task_ids, ignore_case=True, match_middle=True)
    
    print("Select a task ID to view the completion:")
    selected_task_id = prompt('Task ID: ', completer=task_completer)
    
    selected_task = next((item for item in data if item['task_id'] == selected_task_id), None)
    if selected_task:
        print("Completion for Task ID", selected_task_id, ":\n", selected_task['completion'])
    else:
        print("No task found with ID:", selected_task_id)

def interactive_select_task(data):
    """Allows user to interactively select a task and view its completion."""
    task_ids = [entry['task_id'] for entry in data]
    task_completer = WordCompleter(task_ids, ignore_case=True, match_middle=True)
    
    print("Select a task ID to view the completion:")
    selected_task_id = prompt('Task ID: ', completer=task_completer)
    
    selected_task = next((item for item in data if item['task_id'] == selected_task_id), None)
    if selected_task:
        print("Completion for Task ID", selected_task_id, ":\n", selected_task['completion'])
    else:
        print("No task found with ID:", selected_task_id)

def interactive_select_failed_task(data):
    """Interactive interface to select a failed task and view its completion."""
    failed_tasks = list_failed_tasks(data)
    if not failed_tasks:
        print("No failed tasks.")
        return
    
    # Prepare the list for radiolist dialog
    task_ids = [(task['task_id'], f"{task['task_id']}") for task in failed_tasks]
    selected_task_id = radiolist_dialog(
        title="Select Task ID",
        text="Choose a task ID to view its completion:",
        values=task_ids,
    ).run()

    # Find and display the selected task's completion
    if selected_task_id:
        task = next((t for t in failed_tasks if t['task_id'] == selected_task_id), None)
        if task:
            print(f"Completion for {selected_task_id}:\n{task['completion']}")
        else:
            print("Task not found.")
    else:
        print("No task selected.")

# -----------------------------------------------------------------------------------------
def main_menu(data):
    """Provide a menu for the user to choose actions."""
    while True:
        print("\nMenu:")
        print("1. Interactive task selection")
        print("2. Find task by ID")
        print("3. List all failed tasks")
        print("4. Show pass rate")
        print("5. Exit")
        choice = input("Choose an option (1, 2, 3, 4, 5): ")
        
        if choice == "1":
            interactive_select_failed_task(data)
        elif choice == "2":
            # task_id = input("Enter the number for the task ID (HumanEval/{number}): ")
            find_task_by_id(data)
        elif choice == "3":
            failed_tasks = list_failed_tasks(data)
            if not failed_tasks:
                print("No failed tasks.")
            else:
                for task in failed_tasks:
                    print(f"Task ID: {task['task_id']},\tFunction: {task['function_name']}({task['inputs']})")
        elif choice == "4":
            pass_rate = calculate_pass_rate(data)
            print(f"Total pass rate: {pass_rate:.2f}%")
        elif choice == "5":
            break
        else:
            print("Invalid choice, please select 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_jsonl_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    data = load_data(file_path)
    if isinstance(data, str):
        print("Error reading the file:", data)
        sys.exit(1)
    
    main_menu(data)

# ---------------------------------------------------------------------------
# import json
# import sys

# def load_data(file_path):
#     """Load the data from a .jsonl file."""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             data = [json.loads(line) for line in file]
#         return data
#     except Exception as e:
#         return str(e)

# def list_failed_tasks(data):
#     """List the tasks where 'passed' is False, along with their 'task_id' and the function name from 'completion'."""
#     failed_tasks = []
#     for entry in data:
#         if not entry['passed']:
#             function_name = entry['completion'].split('def ')[1].split('(')[0].strip() if 'def ' in entry['completion'] else "Unknown Function"
#             inputs = entry['completion'].split('(')[1].split(')')[0].strip() if '(' in entry['completion'] and ')' in entry['completion'] else "No inputs"
#             failed_tasks.append({'task_id': entry['task_id'], 'function_name': function_name, 'inputs': inputs})
#     return failed_tasks

# def calculate_pass_rate(data):
#     """Calculate and return the pass rate for the dataset."""
#     total = len(data)
#     passed = sum(1 for entry in data if entry['passed'])
#     pass_rate = (passed / total) * 100 if total > 0 else 0
#     return pass_rate

# def find_task_by_id(data, task_id):
#     """Find a task by its ID and print its completion."""
#     task_prefix = f"HumanEval/{task_id}"
#     task = next((item for item in data if item['task_id'] == task_prefix), None)
#     if task:
#         print("Completion for Task ID", task_prefix, ":\n", task['completion'])
#     else:
#         print("No task found with ID:", task_prefix)

# def main_menu(data):
#     """Provide a menu for the user to choose actions."""
#     while True:
#         print("\nMenu:")
#         print("1. List all failed tasks")
#         print("2. Show pass rate")
#         print("3. Find task by ID")
#         print("4. Exit")
#         choice = input("Choose an option (1, 2, 3, 4): ")
        
#         if choice == "1":
#             failed_tasks = list_failed_tasks(data)
#             if not failed_tasks:
#                 print("No failed tasks.")
#             else:
#                 for task in failed_tasks:
#                     print(f"Task ID: {task['task_id']}, Function: {task['function_name']}({task['inputs']})")
#         elif choice == "2":
#             pass_rate = calculate_pass_rate(data)
#             print(f"Total pass rate: {pass_rate:.2f}%")
#         elif choice == "3":
#             task_id = input("Enter the number for the task ID (HumanEval/{number}): ")
#             find_task_by_id(data, task_id)
#         elif choice == "4":
#             break
#         else:
#             print("Invalid choice, please select 1, 2, 3, or 4.")

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python script_name.py <path_to_jsonl_file>")
#         sys.exit(1)
    
#     file_path = sys.argv[1]
#     data = load_data(file_path)
#     if isinstance(data, str):
#         print("Error reading the file:", data)
#         sys.exit(1)
    
#     main_menu(data)