from npmai_agents import AgentBrain
from agent_core import CredStore, Workspace, ToolResult, LLMBackend, Ollama_Local, OpenAIBackend, AnthropicBackend, GeminiBackend, GroqBackend, MistralBackend, CohereBackend, AzureOpenAIBackend, BedrockBackend, HuggingFaceBackend, LlamaCppBackend
import typer

app = typer.Typer()

agent = Agent()
cred = CredStore()
worksapce = Worksapce()

@app.command()
def config_agent(log_cb:Callable=None, progress_cb:Callable=None, status_cb:Callable=None, planner: LLMBackend = None, tool_manager: LLMBackend = None, coder: LLMBackend = None, auditor: LLMBackend = None, verifier: LLMBackend = None, chatter: LLMBackend = None):
  global agent
  agent = Agent(log_cb=log_cb, progress_cb=progress_cb,
                status_cb=status_cb, planner=planner, tool_manager=tool_manager, coder=coder,
                 auditor=auditor, verifier=verifier, chatter=chatter)


@app.command()
def save_credentials(name:str,data:dict):
  saved = cred.save(name=name,data=data)

@app.command()
def load_credentials(name:str):
  load = cred.load(name=name)
  print(load)

@app.command()
def all_credentials():
  all_keys = cred.all_keys()
  print(all_keys)

@app.command()
def workspace_scan():
  scan = workspace.scan()
  print(scan)

@app.command()
def workspace_update(key, value):
  update = workspace.update_profile(key=key,value=value)

@app.command()
def workspace_context():
  ctx_summary = workspace.context_summary()
  print(ctx_summary)

@app.command()
def run(task:str):
  task_result = agent.run_task(task:task)
  return task_result

@app.command()
def chat(user_msg):
  chat_resp = agent.chat(user_msg=user_msg)
  return chat_resp
