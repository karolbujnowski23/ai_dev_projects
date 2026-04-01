import sys
sys.path.append('c:/Users/buyak/Documents/AI_devs/zadania/Z0401')
from src.tools import execute_tool
payload = '{"action": "update", "page": "incydenty", "id": "380792b2c86d9c5be670b3bde48e187b", "title": "MOVE03 Skolwin", "content": "W okolicach Skolwin zauważono bobry."}'
print(execute_tool('send_oko_action', {'action_payload': payload}))
payload2 = '{"action": "done"}'
print(execute_tool('send_oko_action', {'action_payload': payload2}))
