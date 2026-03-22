from dotenv import load_dotenv
load_dotenv()

from agent import agent

def main():
    answer = agent("Write up the specs for the AirPods Max 2, which were released yesterday.")
    print(answer)

if __name__ == "__main__":
    main()