import os
import uuid

from .LLMBaseGenerator import LLMGenerator

class LLMProgrammer(LLMGenerator):
    """
    Responsible for generating source code based on specified requirements using a large language model.
    """
    def generate_code(self, question):
        """
        Generate code using a language model based on a provided prompt.
        """
        prompt_file = "prompt_code_generate.txt"

        additional_prompt = self._read_prompt_file(prompt_file)
        # prompt = f"\n{additional_prompt}\n{question}\n"
        prompt = additional_prompt.format(question=question)

        self.data_dict['prompt_code_generation'] = prompt


        print('Generating code... ',end='')
        output = self.generate(question, prompt_file)
        print('Code generated.\n')

        test_output_str = output['output'].strip('```python').strip('```').strip()

        universal_imports = """import os
import sys
import json
import re
import math
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from typing import List, Dict, Tuple, Optional, Set, Union, Callable
import numpy as np
import pandas as pd
import statistics
from fractions import Fraction
from decimal import Decimal
import re
import hashlib
import pathlib
import copy
from itertools import permutations, combinations, chain
"""

        self.data_dict['code'] = universal_imports + test_output_str

        self.data_dict['response_code'] = output['output']

        return output
    
    def regenerate(self):
        """
        Regenerate code using a language model based on a provided prompt.
        """
        #初始化 data_dict
        self.initialize_data_dict()

        prompt_file = "prompt_regenerate_code.txt"
        question = self.data_dict['prompt']
        correct_test_cases = self.data_dict['passed_list']

        additional_prompt = self._read_prompt_file(prompt_file)
        # prompt = f"\n{additional_prompt}\n{question}\n"
        prompt = additional_prompt.format(question=question,correct_test_cases=correct_test_cases)

        self.data_dict['prompt_code_generation'] = prompt


        print('Regenerating code...')
        output = self.generate(question, prompt_file)
        print('Code regenerated.\n')

        code_output_str = output['output'].strip('```python').strip('```').strip()
        
        universal_imports = """import os
import sys
import json
import re
import math
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from typing import List, Dict, Tuple, Optional, Set, Union, Callable
import numpy as np
import pandas as pd
import statistics
from fractions import Fraction
from decimal import Decimal
import re
import hashlib
import pathlib
import copy
from itertools import permutations, combinations, chain
"""

        self.data_dict['code'] = universal_imports + code_output_str
        self.data_dict['response_code'] = output['output']

        return self.data_dict['judge_id']

    def initialize_data_dict(self):
        """
        Initialize the data_dict with the provided data.
        """
        self.data_dict["parent_id"] = self.data_dict["judge_id"]
        self.data_dict["judge_id"] = str(uuid.uuid4())
        self.data_dict["code_error"] = False
        self.data_dict["code_error_message"] = ""
        self.data_dict["code"] = ""
        self.data_dict["test_list"] = self.data_dict["passed_list"] 
        self.data_dict["passed_list"] = []
        self.data_dict["error_list"] = {}
        self.data_dict["prompt_judge_generate"] = ""
        self.data_dict["response_judge"] = []
        self.data_dict["vote"] = {"A":0,"B":0,"C":0}
        self.data_dict["passed"] = False
        self.data_dict["api_cost"] = 0
        self.data_dict["process_time"] = 0

        return
    