"""
CUA Agent
=========

Agent implementation matching Azure CUA sample for managing the Computer Use
Assistant conversation loop and action execution.
"""

import asyncio
import inspect
import json
import re
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
import openai

logger = logging.getLogger(__name__)


class Agent:
    """CUA agent to start and continue task execution"""

    def __init__(self, client, model: str, computer, logger_instance=None):
        self.client = client
        self.model = model
        self.computer = computer
        self.logger = logger_instance or logger
        self.tools = {}
        self.extra_headers = None
        self.parallel_tool_calls = False
        self.response = None
        self.start_task()

    def add_tool(self, tool: Dict, func) -> None:
        """Add a custom tool to the agent."""
        name = tool["name"]
        self.tools[name] = (tool, func)

    @property
    def requires_user_input(self) -> bool:
        """Check if the agent requires user input."""
        if self.response is None or len(self.response.output) == 0:
            return True
        item = self.response.output[-1]
        return item.type == "message" and item.role == "assistant"

    @property
    def requires_consent(self) -> bool:
        """Check if the agent requires user consent for computer actions."""
        if self.response is None:
            return False
        return any(item.type == "computer_call" for item in self.response.output)

    @property
    def pending_safety_checks(self) -> List[str]:
        """Get pending safety checks."""
        if self.response is None:
            return []
        items = [item for item in self.response.output if item.type == "computer_call"]
        return [check for item in items for check in item.pending_safety_checks]

    @property
    def reasoning_summary(self) -> str:
        """Get the reasoning summary from the response."""
        if self.response is None:
            return ""
        items = [item for item in self.response.output if item.type == "reasoning"]
        return "".join([summary.text for item in items for summary in item.summary])

    @property
    def messages(self) -> List[str]:
        """Get messages from the response."""
        result: List[str] = []
        if self.response:
            for item in self.response.output:
                if item.type == "message":
                    for content in item.content:
                        if content.type == "output_text":
                            result.append(content.text)
        return result

    @property
    def actions(self) -> List[Tuple[str, Dict[str, Any]]]:
        """Get actions from the response."""
        if self.response is None:
            return []
        actions = []
        for item in self.response.output:
            if item.type == "computer_call":
                action_args = vars(item.action) | {}
                action = action_args.pop("type")
                if action == "drag":
                    path = [(point.x, point.y) for point in item.action.path]
                    action_args["path"] = path
                actions.append((action, action_args))
        return actions

    def start_task(self) -> None:
        """Start a new task."""
        self.response = None

    async def continue_task(self, user_message: str = "", temperature: Optional[float] = None) -> None:
        """Continue the current task with optional user message."""
        inputs = []
        screenshot = ""
        response_input_param = openai.types.responses.response_input_param
        previous_response = self.response
        previous_response_id = None
        
        if previous_response:
            previous_response_id = previous_response.id
            for item in previous_response.output:
                if item.type == "computer_call":
                    # Execute the computer action
                    action, action_args = self.actions[0]
                    method = getattr(self.computer, action)
                    
                    if action != "screenshot":
                        if inspect.iscoroutinefunction(method):
                            result = await method(**action_args)
                        else:
                            result = method(**action_args)
                    
                    # Take a screenshot after the action
                    screenshot = await self.computer.screenshot()
                    
                    # Create the computer call output
                    output = response_input_param.ComputerCallOutput(
                        type="computer_call_output",
                        call_id=item.call_id,
                        output=response_input_param.ResponseComputerToolCallOutputScreenshotParam(
                            type="computer_screenshot",
                            image_url=f"data:image/png;base64,{screenshot}",
                        ),
                        acknowledged_safety_checks=self.pending_safety_checks,
                    )
                    inputs.append(output)
                    
                elif item.type == "function_call":
                    # Execute custom function
                    tool_name = item.name
                    kwargs = json.loads(item.arguments)
                    
                    if tool_name not in self.tools:
                        raise ValueError(f"Unsupported tool '{tool_name}'.")
                    
                    _, func = self.tools[tool_name]
                    if inspect.iscoroutinefunction(func):
                        result = await func(**kwargs)
                    else:
                        result = func(**kwargs)
                    
                    output = response_input_param.FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps(result),
                    )
                    inputs.append(output)
                    
                elif item.type == "reasoning" or item.type == "message":
                    pass  # These don't require responses
                else:
                    message = f"Unsupported response output type '{item.type}'."
                    raise NotImplementedError(message)

        # Add user message if provided
        if user_message:
            message = response_input_param.Message(role="user", content=user_message)
            inputs.append(message)

        # Call the API with retry logic
        self.response = None
        wait = 0
        retry = 10
        
        while retry > 0:
            retry -= 1
            try:
                await asyncio.sleep(wait)
                kwargs = {
                    "model": self.model,
                    "input": inputs,
                    "previous_response_id": previous_response_id,
                    "tools": self.get_tools(),
                    "reasoning": {"generate_summary": "concise"},
                    "temperature": temperature,
                    "truncation": "auto",
                    "extra_headers": self.extra_headers,
                    "parallel_tool_calls": self.parallel_tool_calls,
                }
                
                if isinstance(self.client, openai.AsyncOpenAI):
                    self.response = await self.client.responses.create(**kwargs)
                else:
                    self.response = self.client.responses.create(**kwargs)
                    
                assert self.response.status == "completed"
                return
                
            except openai.RateLimitError as e:
                match = re.search(r"Please try again in (\d+)s", e.message)
                wait = int(match.group(1)) if match else 10
                if self.logger:
                    self.logger.exception(
                        f"Rate limit exceeded. Waiting for {wait} seconds.",
                        exc_info=e,
                    )
                if retry == 0:
                    raise
                    
            except openai.InternalServerError as e:
                if self.logger:
                    self.logger.exception(
                        f"Internal server error: {e.message}",
                        exc_info=e,
                    )
                if retry == 0:
                    raise

    def get_tools(self) -> List[openai.types.responses.tool_param.ToolParam]:
        """Get all available tools including computer tool."""
        tools = [entry[0] for entry in self.tools.values()]
        return [self.computer_tool(), *tools]

    def computer_tool(self) -> openai.types.responses.ComputerToolParam:
        """Get the computer tool definition."""
        environment = self.computer.environment
        dimensions = self.computer.dimensions

        return openai.types.responses.ComputerToolParam(
            type="computer_use_preview",
            display_width=dimensions[0],
            display_height=dimensions[1],
            environment=environment,
        )
