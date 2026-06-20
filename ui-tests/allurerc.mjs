import { defineConfig } from "allure";

export default defineConfig({
  name: "Zapaska UI Tests",
  output: "./allure-report",
  historyPath: "./.allure/history.jsonl",
  historyLimit: Number(process.env.HISTORY_LIMIT || 20),
});
