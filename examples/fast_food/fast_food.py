# Load ENV VARS from .env if using an OpenAI or Huggingface API key
from dotenv import load_dotenv
load_dotenv()

# Import and activate package
import aiimports
# Blacklist any modules that should not be generated and will raise an ImportError without modification
aiimports.blacklist_module("django.*")
# Activate the module with the default cache directory
aiimports.activate()

from foods.cheeseburgers import make_burger, buy_burgers


def main():
    # The exact implementations of these functions will differ between generations
    made = make_burger("beef", "american", ["pepperino", "butterfly"])
    bought = buy_burgers(4)
    print(made, bought)


if __name__ == '__main__':
    main()
