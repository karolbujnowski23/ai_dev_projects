import { agent } from "./agent.js";

const answer = await agent("Write up the specs for the AirPods Max 2, which were released yesterday.");
console.log(answer);