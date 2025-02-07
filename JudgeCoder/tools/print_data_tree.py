import json
from collections import defaultdict
import re
import sys

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def build_tree(data):
    tree = defaultdict(lambda: {'children': [], 'data': None})
    root_ids = []

    for item in data:
        judge_id = item['judge_id']
        parent_id = item['parent_id']

        # 存储节点信息
        tree[judge_id]['data'] = item
        
        # 构建父子关系
        if parent_id:
            tree[parent_id]['children'].append(judge_id)
        else:
            # 如果没有父节点 ID，则认为是根节点
            root_ids.append(judge_id)

    # 添加一个全局的根节点，名称为 JudgeCoder
    root_judge_coder = "JudgeCoder"
    tree[root_judge_coder] = {'children': root_ids, 'data': {'judge_id': root_judge_coder, 'code': 'def Judge_Coder(ROOT)', 'passed': True, 'api_cost': 0}}

    return tree, root_judge_coder

def extract_function_signature(code):
    match = re.search(r'def (\w+)\((.*?)\)', code)
    if match:
        return f"{match.group(1)}({match.group(2)})"
    return "unknown_function()"

def calculate_api_cost(tree, node_id):
    node = tree[node_id]
    total_cost = node['data'].get('api_cost', 0)
    for child_id in node['children']:
        total_cost += calculate_api_cost(tree, child_id)
    node['data']['total_api_cost'] = total_cost
    return total_cost

# def print_tree(tree, node_id, prefix="", last=True):
#     node = tree[node_id]
#     passed = node['data'].get('passed', False)
#     pass_symbol = "✅ " if passed else "❌ "
#     connector = "└── " if last else "├── "
#     current_prefix = f"{prefix}{connector}{pass_symbol}"
    
#     if node['data']:
#         function_signature = extract_function_signature(node['data'].get('code', ''))
#         judge_id = node['data']['judge_id']
#         total_api_cost = node['data'].get('total_api_cost', 0)
#         this_time_api_cost = node['data'].get('api_cost', 0)
#         generated_time = node['data'].get('generated_time', 'No Data')
#         print(f"{current_prefix}[{function_signature}]\t[ Generated time: {generated_time} | Total api cost: {total_api_cost} | this time cost: {this_time_api_cost} | judge_id: {judge_id}]")

#     child_count = len(node['children'])
#     for i, child_id in enumerate(node['children']):
#         new_prefix = prefix + ("    " if last else "│   ")
#         print_tree(tree, child_id, new_prefix, i == child_count - 1)

def print_tree(tree, node_id, prefix="", last=True):
    node = tree[node_id]
    passed = node['data'].get('passed', False)
    pass_symbol = "✅ " if passed else "❌ "
    connector = "└── " if last else "├── "
    current_prefix = f"{prefix}{connector}{pass_symbol}"
    
    if node['data']:
        function_signature = extract_function_signature(node['data'].get('code', ''))
        judge_id = node['data']['judge_id']
        total_api_cost = node['data'].get('total_api_cost', 0)
        this_time_api_cost = node['data'].get('api_cost', 0)
        generated_time = node['data'].get('generated_time', 'No Data')
        
        # 判斷 passed 狀態
        if passed:
            print(f"{current_prefix}[{function_signature}]\t[Generated time: {generated_time} | Total api cost: {total_api_cost} | This time cost: {this_time_api_cost} | Judge ID: {judge_id} | Test passed!]")
        else:
            vote = node['data'].get('vote', {})
            highest_vote = max(vote, key=vote.get, default="No votes") if vote else "No votes"
            highest_vote_count = vote[highest_vote] if vote else 0
            print(f"{current_prefix}[{function_signature}]\t[Generated time: {generated_time} | Total api cost: {total_api_cost} | This time cost: {this_time_api_cost} | Judge ID: {judge_id} | Highest Vote: {highest_vote} ({highest_vote_count} votes)]")

    child_count = len(node['children'])
    for i, child_id in enumerate(node['children']):
        new_prefix = prefix + ("    " if last else "│   ")
        print_tree(tree, child_id, new_prefix, i == child_count - 1)



def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_json_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]  # 取得 JSON 文件路徑
    data = read_json_file(file_path)
    
    tree, root_judge_coder = build_tree(data)
    calculate_api_cost(tree, root_judge_coder)  # Calculate total API costs for all nodes
    
    #印出樹狀結構
    print_tree(tree, root_judge_coder)


if __name__ == "__main__":
    main()



# import json
# from collections import defaultdict
# import re

# def read_json_file(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return json.load(file)

# def build_tree(data):
#     tree = defaultdict(lambda: {'children': [], 'data': None})
#     root_ids = []

#     for item in data:
#         judge_id = item['judge_id']
#         parent_id = item['parent_id']

#         # 存储节点信息
#         tree[judge_id]['data'] = item
        
#         # 构建父子关系
#         if parent_id:
#             tree[parent_id]['children'].append(judge_id)
#         else:
#             # 如果没有父节点 ID，则认为是根节点
#             root_ids.append(judge_id)

#     # 添加一个全局的根节点，名称为 JudgeCoder
#     root_judge_coder = "JudgeCoder"
#     tree[root_judge_coder] = {'children': root_ids, 'data': {'judge_id': root_judge_coder, 'code': 'def judge_coder():', 'passed': True}}

#     return tree, root_judge_coder

# def extract_function_name(code):
#     # 正则表达式匹配 Python 函数定义
#     match = re.search(r'def (\w+)\((.*?)\)', code)
#     if match:
#         return match.group(1)  # 返回函数名称
#     return "unknown_function"  # 未找到匹配时返回默认值

# def print_tree(tree, node_id, prefix="", last=True):
#     node = tree[node_id]
#     passed = node['data'].get('passed', False)  # 获取 pass 字段
#     pass_symbol = "〇 " if passed else "✖ "
    
#     connector = "└── " if last else "├── "
#     current_prefix = f"{prefix}{connector}{pass_symbol}"
    
#     if node['data']:
#         function_name = extract_function_name(node['data'].get('code', ''))
#         judge_id = node['data']['judge_id']
#         print(f"{current_prefix}[{function_name}()](judge_id: {judge_id})")

#     child_count = len(node['children'])
#     for i, child_id in enumerate(node['children']):
#         new_prefix = prefix + ("    " if last else "│   ")
#         print_tree(tree, child_id, new_prefix, i == child_count - 1)

# def main():
#     file_path = 'human-eval/LLModifier/human_Eval_Results_old/JudgeCoder_History/0515_output.json'  # JSON 文件路径
#     data = read_json_file(file_path)
    
#     tree, root_judge_coder = build_tree(data)
    
#     # 打印树状结构，从 JudgeCoder 根节点开始
#     print_tree(tree, root_judge_coder)

# if __name__ == "__main__":
#     main()


# import json
# from collections import defaultdict
# import re

# def read_json_file(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return json.load(file)

# def build_tree(data):
#     tree = defaultdict(lambda: {'children': [], 'data': None})
#     root_ids = []

#     for item in data:
#         judge_id = item['judge_id']
#         parent_id = item['parent_id']

#         # 存储节点信息
#         tree[judge_id]['data'] = item
        
#         # 构建父子关系
#         if parent_id:
#             tree[parent_id]['children'].append(judge_id)
#         else:
#             # 如果没有父节点 ID，则认为是根节点
#             root_ids.append(judge_id)

#     # 添加一个全局的根节点，名称为 JudgeCoder
#     root_judge_coder = "JudgeCoder"
#     tree[root_judge_coder] = {'children': root_ids, 'data': {'judge_id': root_judge_coder, 'code': 'def judge_coder():'}}

#     return tree, root_judge_coder

# def extract_function_name(code):
#     # 正则表达式匹配 Python 函数定义
#     match = re.search(r'def (\w+)\(', code)
#     if match:
#         return match.group(1)  # 返回函数名称
#     return "unknown_function"  # 未找到匹配时返回默认值

# def print_tree(tree, node_id, prefix="", last=True):
#     node = tree[node_id]
#     connector = "└── " if last else "├── "
#     current_prefix = f"{prefix}{connector}"
    
#     if node['data']:
#         function_name = extract_function_name(node['data'].get('code', ''))
#         judge_id = node['data']['judge_id']
#         print(f"{current_prefix}[{function_name}()](judge_id: {judge_id})")

#     child_count = len(node['children'])
#     for i, child_id in enumerate(node['children']):
#         new_prefix = prefix + ("    " if last else "│   ")
#         print_tree(tree, child_id, new_prefix, i == child_count - 1)

# def main():
#     file_path = 'human-eval/LLModifier/human_Eval_Results_old/JudgeCoder_History/0515_output.json'  # JSON 文件路径
#     data = read_json_file(file_path)
    
#     tree, root_judge_coder = build_tree(data)
    
#     # 打印树状结构，从 JudgeCoder 根节点开始
#     print_tree(tree, root_judge_coder)

# if __name__ == "__main__":
#     main()



# import json
# from collections import defaultdict
# import re

# def read_json_file(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return json.load(file)

# def build_tree(data):
#     tree = defaultdict(lambda: {'children': [], 'data': None})
#     root_ids = []

#     for item in data:
#         judge_id = item['judge_id']
#         parent_id = item['parent_id']

#         # 存储节点信息
#         tree[judge_id]['data'] = item
        
#         # 构建父子关系
#         if parent_id:
#             tree[parent_id]['children'].append(judge_id)
#         else:
#             # 如果没有父节点 ID，则认为是根节点
#             root_ids.append(judge_id)

#     return tree, root_ids

# def extract_function_name(code):
#     # 正则表达式匹配 Python 函数定义
#     match = re.search(r'def (\w+)\(', code)
#     if match:
#         return match.group(1)  # 返回函数名称
#     return "unknown_function"  # 未找到匹配时返回默认值

# def print_tree(tree, node_id, prefix="", last=True):
#     node = tree[node_id]
#     connector = "   └── " if last else "├── "
#     current_prefix = f"{prefix}{connector}"
    
#     if node['data']:
#         function_name = extract_function_name(node['data'].get('code', ''))
#         judge_id = node['data']['judge_id']
#         print(f"{current_prefix}[{function_name}()](judge_id: {judge_id})")

#     child_count = len(node['children'])
#     for i, child_id in enumerate(node['children']):
#         new_prefix = prefix + ("    " if last else "│   ")
#         print_tree(tree, child_id, new_prefix, i == child_count - 1)

# def main():
#     file_path = 'human-eval/LLModifier/JudgeCoder/output.json'  # JSON 文件路径
#     data = read_json_file(file_path)
    
#     tree, root_ids = build_tree(data)
    
#     # 打印树状结构
#     for root_id in root_ids:
#         print_tree(tree, root_id)

# if __name__ == "__main__":
#     main()

