import sys
from agent import main

if __name__ == "__main__":
    print("Starting Failure Log Recovery Agent...")
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Agent] Process interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[Agent] Unhandled error occurred: {e}")
        sys.exit(1)