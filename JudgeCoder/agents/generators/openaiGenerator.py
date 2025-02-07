from .baseAbstractGenerator import CommandGenerator
import openai # type: ignore
import time
from tqdm import tqdm # type: ignore
import threading



class OpenAIGenerator(CommandGenerator):
    """
    Command generator that uses OpenAI's API to generate output based on instructions.
    """

    def __init__(self, api_key: str, model="gpt-3.5-turbo"):
        """
        Initialize the generator with the necessary API key and default engine.
        
        :param api_key: OpenAI API key.
        :param engine: The default engine to use for generation (default is "davinci-codex").
        """
        self.api_key = api_key
        openai.api_key = self.api_key
        self.model = model
        self.temperature = 0.2  # Default temperature

    def set_temperature(self, temperature: float):
        """
        Set the temperature for the generation process.
        
        :param temperature: A float indicating the randomness of the output.
                            Lower values make the output more deterministic.
        """
        self.temperature = temperature

    def set_model(self, model: str):
        """
        Set the model for the generation process.
        
        :param model: A string specifying the model to use for generation.
        """
        self.model = model

    def generate(self, instruction: str, max_tokens: int = 4096) -> dict:
        """
        Generate output using OpenAI's API based on the provided instruction,
        and return both the generated output and the token usage.
        
        :param instruction: The instruction to generate output for.
        :param max_tokens: The maximum number of tokens to generate.
        :return: A dictionary containing the generated output and the token usage.
        """


        client = openai.OpenAI(api_key = self.api_key)


        # ------ 原版 code ------

        start_time = time.time()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": instruction}],
            max_tokens=max_tokens,
            temperature=self.temperature
        )
        end_time = time.time()

        output = response.choices[0].message.content
        usage = response.usage.total_tokens
        completion_tokens = response.usage.completion_tokens
        prompt_tokens = response.usage.prompt_tokens

        time_taken = end_time - start_time

        # ------ 原版 code ------


        return {"output": output, "usage": usage, "process_time": time_taken , "completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens }
        # return {"output": "TEST", "usage": 0, "process_time": 0 }

        

"""
        # ------ 加上進度條玩一下 START------

        # Function to call the API
        def call_api():
            nonlocal response
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": instruction}],
                max_tokens=max_tokens,
                temperature=self.temperature
            )

        # Start the API call in a separate thread
        response = None
        api_thread = threading.Thread(target=call_api)
        api_thread.start()


        # Create a tqdm progress bar
        # with tqdm(total=40, desc="Generating output", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}ms]') as pbar:
        with tqdm(total=40, desc="Time:", bar_format='[{elapsed}s]') as pbar:
            start_time = time.time()

            # Update the progress bar while waiting for the API call to complete
            while api_thread.is_alive():
                pbar.update(1)
                time.sleep(0.1)  # Just a small sleep to update the progress bar

            api_thread.join()  # Ensure the API call has completed

        end_time = time.time()

        output = response.choices[0].message.content
        usage = response.usage.total_tokens
        time_taken = end_time - start_time

        # ------ 加上進度條玩一下 END ------
    """
