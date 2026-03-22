import { chat } from "./ai.js";
import * as sum from "./tools/sum.js";
import * as generateImage from "./tools/generate_image.js";
import * as search from "./tools/search.js";
import * as scrape from "./tools/scrape.js";

const tools = [sum, generateImage, search, scrape];
const definitions = tools.map((tool) => tool.definition);

const history = [];

export async function agent(input) {
   history.push({ "role": "user", "content": input });

   for (let i = 0; i < 10; i++) { 
        const answer = await chat(history, definitions);

        history.push(...answer.output);
    
        if (answer.message) {
            return answer.message;
        }
    
        await execute(answer.calls, history);
   }
}

async function execute(calls, history) {
    for (const call of calls) {
        const tool = tools.find((tool) => tool.definition.name === call.name);
        const args = JSON.parse(call.arguments);
        console.log(args);
        const result = await tool.execute(args);
        console.log(result);
        history.push({
            type: "function_call_output",
            call_id: call.call_id,
            output: JSON.stringify(result),
        });
    }
}