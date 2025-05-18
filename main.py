# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Entry point script for the DeerFlow project.
"""

import argparse
import asyncio
import logging
import sys
import os
from datetime import datetime

from InquirerPy import inquirer

from src.config.questions import BUILT_IN_QUESTIONS, BUILT_IN_QUESTIONS_ZH_CN
from src.workflow import run_agent_workflow_async

# Class to redirect stdout/stderr to the logging system
class StreamToLogger:
    def __init__(self, logger_instance, log_level=logging.INFO):
        self.logger = logger_instance
        self.log_level = log_level
        self.line_buffer = ''

    def write(self, buf):
        # Buffer data until a newline is encountered
        self.line_buffer += buf
        while '\n' in self.line_buffer:
            line, self.line_buffer = self.line_buffer.split('\n', 1)
            if line.rstrip(): # Avoid logging empty strings
                self.logger.log(self.log_level, line.rstrip())
        # Log any remaining data in the buffer if the stream is flushed/closed
        # and it doesn't end with a newline (e.g. print(..., end=''))

    def flush(self):
        if self.line_buffer.rstrip():
            self.logger.log(self.log_level, self.line_buffer.rstrip())
            self.line_buffer = ''
        for handler in self.logger.handlers:
            handler.flush()

    def isatty(self):
        # Some libraries check isatty, stdout/stderr should have it
        return False

# Store the original stdout/stderr for the console handler
_original_stdout = sys.stdout
_original_stderr = sys.stderr

# Global variable to store the current file handler for the ask function
current_query_file_handler = None

def ask(
    question,
    debug=False, # This debug flag from args will control console, file will be DEBUG
    max_plan_iterations=1,
    max_step_num=3,
    enable_background_investigation=True,
):
    """Run the agent workflow with the given question.

    Args:
        question: The user's query or request
        debug: If True, enables debug level logging for console
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
        enable_background_investigation: If True, performs web search before planning to enhance context
    """
    global current_query_file_handler
    root_logger = logging.getLogger()
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Remove previous query file handler if it exists
    if current_query_file_handler:
        root_logger.removeHandler(current_query_file_handler)
        current_query_file_handler.close()
        current_query_file_handler = None

    # Create a unique log file name for this query
    LOG_DIR = "logs"
    # Sanitize question for filename (simple version)
    safe_query_part = "".join(c if c.isalnum() else "_" for c in question[:30])
    query_log_file_name = os.path.join(LOG_DIR, datetime.now().strftime(f"query_%Y%m%d_%H%M%S_{safe_query_part}.log"))
    
    current_query_file_handler = logging.FileHandler(query_log_file_name, mode='a')
    current_query_file_handler.setLevel(logging.DEBUG) # Always DEBUG for query file
    current_query_file_handler.setFormatter(log_formatter)
    root_logger.addHandler(current_query_file_handler)
    
    logging.info(f"--- Starting new query --- ")
    logging.info(f"Query: {question}")
    logging.info(f"Logging for this query will be in: {query_log_file_name}")

    try:
        asyncio.run(
            run_agent_workflow_async(
                user_input=question,
                debug=debug, # Pass the console debug flag to workflow
                max_plan_iterations=max_plan_iterations,
                max_step_num=max_step_num,
                enable_background_investigation=enable_background_investigation,
            )
        )
    finally:
        logging.info(f"--- Query processing finished. Log file: {query_log_file_name} ---")
        if current_query_file_handler:
            root_logger.removeHandler(current_query_file_handler)
            current_query_file_handler.close()
            current_query_file_handler = None

def main(
    debug=False,
    max_plan_iterations=1,
    max_step_num=3,
    enable_background_investigation=True,
):
    """Interactive mode with built-in questions.

    Args:
        enable_background_investigation: If True, performs web search before planning to enhance context
        debug: If True, enables debug level logging for console
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
    """
    # First select language
    language = inquirer.select(
        message="Select language / 选择语言:",
        choices=["English", "中文"],
    ).execute()

    # Choose questions based on language
    questions = (
        BUILT_IN_QUESTIONS if language == "English" else BUILT_IN_QUESTIONS_ZH_CN
    )
    ask_own_option = (
        "[Ask my own question]" if language == "English" else "[自定义问题]"
    )

    # Select a question
    initial_question = inquirer.select(
        message=(
            "What do you want to know?" if language == "English" else "您想了解什么?"
        ),
        choices=[ask_own_option] + questions,
    ).execute()

    if initial_question == ask_own_option:
        initial_question = inquirer.text(
            message=(
                "What do you want to know?"
                if language == "English"
                else "您想了解什么?"
            ),
        ).execute()

    # Pass all parameters to ask function
    ask(
        question=initial_question,
        debug=debug,
        max_plan_iterations=max_plan_iterations,
        max_step_num=max_step_num,
        enable_background_investigation=enable_background_investigation,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Deer")
    parser.add_argument("query", nargs="*", help="The query to process")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode with built-in questions",
    )
    parser.add_argument(
        "--max_plan_iterations",
        type=int,
        default=1,
        help="Maximum number of plan iterations (default: 1)",
    )
    parser.add_argument(
        "--max_step_num",
        type=int,
        default=3,
        help="Maximum number of steps in a plan (default: 3)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging for console")
    parser.add_argument(
        "--no-background-investigation",
        action="store_false",
        dest="enable_background_investigation",
        help="Disable background investigation before planning",
    )

    args = parser.parse_args()

    # --- Initial Logging Setup (Console and stdout/stderr redirection) ---
    LOG_DIR = "logs"
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    console_log_level = logging.DEBUG if args.debug else logging.INFO
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG) # Root logger at DEBUG to capture everything for file handlers

    # Clear any pre-existing handlers (e.g., from previous runs in an interactive session if module reloaded)
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    # Console Handler: logs messages to original stderr
    console_handler = logging.StreamHandler(_original_stderr) 
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # Redirect stdout and stderr to the logger
    sys.stdout = StreamToLogger(root_logger, logging.INFO)
    sys.stderr = StreamToLogger(root_logger, logging.ERROR)
    
    logging.info(f"Initial logging setup complete. Console log level: {logging.getLevelName(console_log_level)}")
    logging.debug("Debug mode enabled for console.") # This will only show if console_log_level is DEBUG
    # --- Logging Setup End ---

    if args.interactive:
        # Pass command line arguments to main function
        main(
            debug=args.debug,
            max_plan_iterations=args.max_plan_iterations,
            max_step_num=args.max_step_num,
            enable_background_investigation=args.enable_background_investigation,
        )
    else:
        # Parse user input from command line arguments or user input
        if args.query:
            user_query = " ".join(args.query)
        else:
            user_query = input("Enter your query: ")

        # Run the agent workflow with the provided parameters
        ask(
            question=user_query,
            debug=args.debug,
            max_plan_iterations=args.max_plan_iterations,
            max_step_num=args.max_step_num,
            enable_background_investigation=args.enable_background_investigation,
        )
