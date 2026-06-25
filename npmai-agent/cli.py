import os, sys, json, re, shutil, subprocess, tempfile, traceback
import threading, time, smtplib, imaplib, email as email_lib
import hashlib, base64, platform, glob, zipfile, tarfile
from npmai import Ollama, Memory
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional
from abc import ABC, abstractmethod
from Tools_Developer_CLI import GitTool, GitHubTool, GitLabTool, DockerTool, PackageManagerTool, VSCodeTool, TerminalTool, MakefileTool, CMakeTool, DebuggerTool
from Tools_business import StripeTool, RazorpayTool, ShopifyTool, InvoiceTool, AccountingTool, CRMTool, EmailMarketingTool, AnalyticsTool, InventoryTool, ContractTool
from Tools_cloud_devops import AWSS3Tool, AWSLambdaTool, AWSECSTool, CloudflareTool, VercelTool, NetlifyTool, RailwayTool, KubernetesTool, TerraformTool, MonitoringTool
from Tools_communication_extended import MicrosoftTeamsTool, ZoomTool, TwilioTool, SendGridTool, PushNotificationTool, RSSFeedTool, WebhookTool, CalendarTool, ChatOpsAutomationTool, SMTPAdvancedTool
from Tools_creative import FigmaTool, BlenderTool, SVGTool, CanvaTool, FontTool, ColorTool, IconTool, DiagramTool, PrintTool, ThreeDTool
from Tools_data_research import DataAnalysisTool, VisualizationTool, WebScrapingAdvancedTool, SearchResearchTool, FinancialDataTool, SocialMediaDataTool, WeatherGeoTool, TextAnalyticsTool, DatabaseTool, ReportGeneratorTool
from Tools_media import FFmpegTool, YouTubeDownloaderTool, AudioTool, ImageAdvancedTool, ScreenRecorderTool, TextToSpeechTool, VideoEditingTool, PodcastTool, StreamingTool, MediaMetadataTool
from Tools_productivity import GoogleWorkspaceTool, NotionAdvancedTool, LinearTool, AsanaTool, TrelloTool, ClickUpTool, TodoistTool, ObsidianTool, BookmarkManagerTool, TimeTrackingTool
from Tools_security_ai import SecurityScannerTool, CryptographyTool, PenetrationTestingTool, AIImageGenerationTool, AITextGenerationAdvancedTool, MLModelTool, SpeechAITool, ComputerVisionTool, AutomationWorkflowTool, KnowledgeBaseTool
from Tools_system_hardware import SystemAdvancedTool, NetworkAdvancedTool, FileSystemAdvancedTool, ProcessAutomationTool, PrinterTool, ClipboardAdvancedTool, HardwareMonitorTool, RaspberryPiTool, MQTTIoTTool, VirtualizationTool
from npmai_agents import AgentBrain
from agent_core import CredStore, Workspace, ToolResult, LLMBackend, Ollama_Local, OpenAIBackend, AnthropicBackend, GeminiBackend, GroqBackend, MistralBackend, CohereBackend, AzureOpenAIBackend, BedrockBackend, HuggingFaceBackend, LlamaCppBackend
import typer
import json

app = typer.Typer()

_agent = AgentBrain()
_cred = CredStore()
_workspace = Workspace()

@app.command()
def config_agent(
    planner_model: str = "llama3.2:3b",
    planner_provider: str = "npmai",
    coder_model: str = "codellama:7b-instruct", 
    coder_provider: str = "npmai",
    auditor_model: str = "qwen2.5-coder:7b",
    auditor_provider: str = "npmai",
    verifier_model: str = "llama3.2:3b",
    verifier_provider: str = "npmai",
    chatter_model: str = "granite3.3:2b",
    chatter_provider: str = "npmai",
):
    global _agent
    
    def build_backend(provider: str, model: str):
        p = provider.lower()
        if p == "npmai":       return Ollama(model=model)
        elif p == "local":     return Ollama_Local(model=model)
        elif p == "openai":    return OpenAIBackend(model=model, api_key=CredStore.load("openai")["api_key"])
        elif p == "groq":      return GroqBackend(model=model, api_key=CredStore.load("groq")["api_key"])
        elif p == "anthropic": return AnthropicBackend(model=model, api_key=CredStore.load("anthropic")["api_key"])
        elif p == "gemini":    return GeminiBackend(model=model, api_key=CredStore.load("gemini")["api_key"])
        elif p == "mistral":   return MistralBackend(model=model, api_key=CredStore.load("mistral")["api_key"])
        elif p == "cohere":    return CohereBackend(model=model, api_key=CredStore.load("cohere")["api_key"])
        elif p == "azure":     return AzureOpenAIBackend(model=model, **CredStore.load("azure"))
        elif p == "bedrock":   return BedrockBackend(model=model, **CredStore.load("bedrock"))
        elif p == "hf":        return HuggingFaceBackend(model=model, api_key=CredStore.load("hf")["api_key"])
        elif p == "llamacpp":  return LlamaCppBackend(model=model)
        else: raise typer.BadParameter(f"Unknown provider '{provider}'. Use: npmai, local, openai, groq, anthropic, gemini, mistral, cohere, azure, bedrock, hf, llamacpp")
    
    _agent = AgentBrain(
        planner  = build_backend(planner_provider,  planner_model),
        coder    = build_backend(coder_provider,    coder_model),
        auditor  = build_backend(auditor_provider,  auditor_model),
        verifier = build_backend(verifier_provider, verifier_model),
        chatter  = build_backend(chatter_provider,  chatter_model),
    )
    print("Agent configured.")


@app.command()
def save_credentials(name:str,data:str):
  data_parsed = json.loads(data)
  saved = _cred.save(name=name,data=data)

@app.command()
def load_credentials(name:str):
  load = _cred.load(name=name)
  print(load)

@app.command()
def all_credentials():
  all_keys = _cred.all_keys()
  print(all_keys)

@app.command()
def workspace_scan():
  scan = _workspace.scan()
  print(scan)

@app.command()
def workspace_update(key, value):
  update = _workspace.update_profile(key=key,value=value)

@app.command()
def workspace_context():
  ctx_summary = _workspace.context_summary()
  print(ctx_summary)

@app.command()
def run(task:str):
  task_result = _agent.run_task(task=task)
  return task_result

@app.command()
def chat(user_msg:str):
  chat_resp = _agent.chat(user_msg=user_msg)
  return chat_resp
