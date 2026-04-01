# Exploration and Testing Scripts

This directory contains various scripts created during the development and problem-solving process for the `windpower` task. They are not part of the final, working solution but are preserved here as a record of the discovery process, particularly the attempts to solve the secondary "mirrored hint" puzzle.

### File Descriptions

*   **`get_docs.py`**: A simple script to call the `get` action with the `documentation` parameter. This was used early on to fetch the turbine's operational specifications, such as power yield curves and safety limits.

*   **`test_get_data.py`**: A script to test the asynchronous `get` and `getResult` flow for retrieving queued data like the weather forecast and powerplant status.

*   **`test_unlock.py`**: A script specifically created to test the `unlockCodeGenerator` action and understand its response format. This was crucial for learning that the API returns `signedParams` which allow for correct mapping of unlock codes to their corresponding configurations.

*   **`get_extra_flag.py` & `get_mirror_flag.py`**: Initial, simple attempts to solve the secondary puzzle by submitting a reversed hint string. These failed due to incorrect payload structure.

*   **`submit_mirrored_hint.py`**: An evolution of the hint-solving scripts. This version experimented with different JSON structures for the final answer payload, leading to the discovery that the `answer` field must be a JSON object and contain a valid `action`.

*   **`find_palindrome_code.py`**: A complex, asynchronous brute-force script developed to test the hypothesis that the secret flag was a palindromic `unlockCode`. It systematically queued requests for all 252 possible valid configurations and checked each resulting code. This script ultimately proved the hypothesis was incorrect but demonstrated the need for batch processing to handle the 40-second session limit.

*   **`gamble_for_flag.py`**: A script created to test the hypothesis that the `"turbine broken by strong wind gusts"` error was a random, probabilistic event. It repeatedly ran the failing sequence in a loop, which ultimately showed the error was deterministic.

*   **`submit_final_flag_pacification.py` & `final_attempt.py`**: Scripts designed to test the "Pacification Hypothesis"—the idea that a harmless action (like `get(documentation)`) could be used to bypass the required but dangerous `turbinecheck` before submitting the `done` command.

*   **`submit_final_flag_safely.py`**: An attempt to solve the "turbine broken" paradox by first configuring the turbine to a safe, idle state before running the required `turbinecheck`. This failed because the configuration process itself was too slow to prevent the simulated wind gusts from breaking the turbine.
