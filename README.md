# CortexShell

CortexShell is an advanced command-line productivity tool designed to streamline your development workflow by leveraging the power of AI Large Language Models (LLMs). With CortexShell, you can generate shell commands, code snippets, comments, and documentation, all within your terminal. Say goodbye to cheat sheets and time-consuming Google searches, as CortexShell delivers accurate answers and suggestions for a wide array of tasks.

CortexShell is compatible with all major operating systems, including Linux, macOS, and Windows. It supports various shells such as PowerShell, CMD, Bash, Zsh, Fish, and more.

## Installation

To install CortexShell, execute the following command:

```shell
pip install cortex-shell
```

Alternatively, you can install CortexShell using `pipx`, which allows you to manage and isolate Python packages in separate environments. By using `pipx`, you can ensure that CortexShell and its dependencies are isolated from your system's Python environment, preventing potential conflicts and making it easier to manage and update. To install CortexShell with `pipx`, run the following command:

```shell
pipx install cortex-shell
```

You will need an OpenAI API key, which you can generate [here](https://platform.openai.com/account/api-keys).

Upon the first run, a default config file will be created. You need to fill in your credentials in the `~/.config/cortex-shell/config.yaml` file.

## Usage

CortexShell offers a variety of use cases, including simple queries, shell queries, and code queries. It can be invoked by executing `cortex-shell` or `c-sh`.

## Input Modes

CortexShell accepts input from the `prompt` argument, stdin, interactively (REPL) and from an editor (`$VISUAL` env variable), allowing you to choose the most convenient method for your preferences.

### Prompt argument

The `prompt` argument is the single, optional argument for CortexShell. It is used to provide a prompt for the desired action or information. Using the `prompt` argument allows you to directly call CortexShell with a question or command, obtaining quick and precise results.

```shell
cortex-shell "nginx default config file location"
# The default configuration file for Nginx is located at /etc/nginx/nginx.conf.
```

```shell
cortex-shell "mass of sun"
# The mass of the Sun is approximately 1.989 x 10^30 kg.
```

```shell
cortex-shell "1 hour and 30 minutes to seconds"
# 1 hour and 30 minutes is equal to 5400 seconds (1 hour) + 1800 seconds (30 minutes) = 7200 seconds
```

### Stdin Input

CortexShell can process data from standard input (stdin), making it easy to analyze and manipulate information from various sources. This section demonstrates how to use stdin input with CortexShell to streamline your data analysis tasks.

For example, you can easily generate a git commit message based on a diff using `cortex-shell`:

```shell
git diff | cortex-shell "Generate a git commit message for my changes"
# Commit message: Refactor prompt argument description
```

You can analyze logs from various sources by passing them through stdin or command-line arguments, along with a user-friendly prompt. This enables you to quickly identify errors and receive suggestions for possible solutions:

```shell
docker logs -n 20 container_name | cortex-shell "check logs, find errors, provide possible solutions"
# ...
```

This powerful feature simplifies the process of managing and understanding data from different sources, allowing you to focus on what really matters: improving your projects and applications.

### REPL Mode

There is a very handy REPL (read–eval–print loop) mode, which allows you to interactively chat with GPT models. To start a chat session in REPL mode, use the `--repl` option. REPL is also the default mode if no `stdin` is provided.

```text
cortex-shell
Entering REPL mode, press Ctrl+C to exit.
> What is REPL?
REPL stands for Read-Eval-Print Loop. It is an interactive programming environment ...
> How can I use Python with REPL?
To use Python with REPL, ...
```

REPL mode can be used in conjunction with the other input modes, except stdin (pipe). The input from other modes will be prepended and shown to you at the beginning:

```text
cortex-shell --repl "tell me about"
Entering REPL mode, press Ctrl+C to exit.
tell me about
> yourself
I am an AI language model designed to assist with programming and system administration tasks.
I can help you with Linux/Arch Linux operating systems and fish shell.
If you have any questions or need assistance, feel free to ask.
```

There is advanced multiline support. You can simply paste texts containing linebreaks:

```text
cortex-shell
Entering REPL mode, press Ctrl+C to exit.
> tell me about
yourself
I am an AI programming and system administration assistant.
I can help you with managing Linux/Arch Linux operating systems and provide assistance with the fish shell.
If you have any questions or need help, feel free to ask.
```

Another possibility is to enter the dedicated multiline-mode by using hotkey `ctrl+e`. In this mode, pressing `Enter` will insert a line break, instead of committing the prompt. `ctrl+d` can then be used to do that.

```text
cortex-shell
Entering REPL mode, press Ctrl+C to exit.
> *press ctrl+e*
>>> tell me about
    yourself

*press ctrl+d*

I am an AI programming and system administration assistant.
I can help you with managing Linux/Arch Linux operating systems and provide assistance with the fish shell.
If you have any questions or need help, feel free to ask.
```

### Editor Mode

CortexShell provides an Editor mode, allowing you to leverage the power of your preferred text editor when composing prompts. This mode is especially useful when working with complex or multiline queries, as it offers a more comfortable and flexible input environment.

To use the Editor mode, simply invoke CortexShell with the `--editor` or `-e` option:

```shell
cortex-shell --editor
```

This command will open your default text editor, as specified by the `$VISUAL` environment variable. Write your prompt in the editor, save the file, and exit the editor. CortexShell will then process your prompt and provide the desired output.

For example, if you want to generate a detailed explanation of a Python function, you can use the Editor mode to comfortably write a multiline prompt:

```text
Explain the following Python function in detail:
def greet(name):
    return f"Hello, {name}!"
```

After saving and exiting the editor, CortexShell will provide a detailed explanation of the function:

```text
The given Python function, `greet`, takes a single argument called `name`. It returns a formatted string that includes the value of `name` within a greeting message. The `f` prefix before the string indicates that it's an f-string, which allows for the easy inclusion of variables within the string using curly braces `{}`. In this case, the `name` variable is embedded in the string, resulting in a personalized greeting, such as "Hello, John!".
```

With the Editor mode, you can enjoy the full capabilities of your text editor while benefiting from CortexShell's powerful AI-driven assistance.

## Shell Commands

If you ever find yourself forgetting common shell commands, such as `chmod`, and needing to look up the syntax online, the `--shell` or shortcut `-s` option can help. With this option, you can quickly find and execute the commands you need right in the terminal.

```shell
cortex-shell --shell "make all files in current directory read only"
# chmod -R a-w .
# (*) [e]xecute ( ) [d]escribe ( ) [a]bort
```

CortexShell is aware of the OS and shell you are using and will provide shell commands specific to your system. For instance, if you ask `cortex-shell` to update your system, it will return a command based on your OS. Here's an example using macOS:

```shell
cortex-shell -s "update my system"
# sudo pacman -Syu
# (*) [e]xecute ( ) [d]escribe ( ) [a]bort
```

The same prompt, when used on Ubuntu, will generate a different suggestion:

```shell
cortex-shell -s "update my system"
# sudo apt update && sudo apt upgrade -y
# (*) [e]xecute ( ) [d]escribe ( ) [a]bort
```

You can ask GPT to describe the suggested shell command, and it will provide a short description of what the command does:

```shell
cortex-shell -s "List all .txt files in the current directory, sorted by access time in descending order."
# ls -ltu *.txt
# ( ) [e]xecute (*) [d]escribe ( ) [a]bort
# • ls: List directory contents
# • -l: Use long listing format
# • -t: Sort by modification time, newest first
# • -u: Use access time instead of modification time for sorting
# • --time=access: Show access time instead of modification time
# • *.txt: Filter for files with .txt extension
# (*) [e]xecute ( ) [d]escribe ( ) [a]bort
```

Let's try some docker containers:

```shell
cortex-shell -s "start nginx using docker, forward 443 and 80 port, mount current folder as document root"
# docker run -d -p 80:80 -p 443:443 -v (pwd):/usr/share/nginx/html --name nginx-container nginx
# (*) [e]xecute ( ) [d]escribe ( ) [a]bort
```

You can still use pipes to pass input to `cortex-shell` and get shell commands as output:

```shell
cat data.json | cortex-shell -s "curl localhost with provided json"
# curl -X POST -H "Content-Type: application/json" -d '{"a": 1, "b": 2, "c": 3}' http://localhost
```

You can apply additional shell magic in your prompt, as shown in this example passing file names to ffmpeg:

```shell
ls
# 1.mp4 2.mp4 3.mp4
cortex-shell -s "using ffmpeg combine multiple videos into one without audio. Video file names: $(ls -m)"
# ffmpeg -i 1.mp4 -i 2.mp4 -i 3.mp4 -filter_complex "[0:v] [1:v] [2:v] concat=n=3:v=1 [v]" -map "[v]" out.mp4
# (*) [e]xecute ( ) [d]escribe ( ) [a]bort
```

REPL mode can work with `--shell` and `--code` options, which makes it very handy for interactive shell commands and code generation:

```text
cortex-shell --shell
Entering REPL mode, press Ctrl+C to exit.
> What is in current folder?
ls
( ) [e]xecute ( ) [d]escribe (*) [a]bort
> Show file sizes
ls -lh
( ) [e]xecute ( ) [d]escribe (*) [a]bort
> Sort files by size
ls -lhS
( ) [e]xecute ( ) [d]escribe (*) [a]bort
```

## Shell Integration

Shell integration allows you to use CortexShell in your terminal with hotkeys. It is currently available for fish, bash, zsh and powershell. It will allow you to have completions for your shell prompt, and also edit suggested commands right away.

To install shell integration, run:

```shell
cortex-shell --install-integration
# Integration for "fish" shell successfully installed. Restart your terminal to apply changes.
```

This will add a few lines to your `~/.config/fish/config.fish`, `.bashrc`, `.zshrc`, or `Microsoft.PowerShell_profile` file. After that, you can use `ctrl+l` to invoke CortexShell. When you do that, it will replace your current input line buffer with the suggested command. You can then edit it and press `Enter` to execute.

## Generating Code

With the `--code` or shortcut `-c` option, you can query only code as output. For example:

```shell
cortex-shell -c "Solve classic fizz buzz problem using Python"
```

```python
def fizz_buzz(n):
    for i in range(1, n+1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)

fizz_buzz(100)
```

Since it is valid Python code, you can redirect the output to a file:

```shell
cortex-shell -c "solve classic fizz buzz problem using Python" > fizz_buzz.py
python fizz_buzz.py
# 1
# 2
# Fizz
# 4
# Buzz
# Fizz
```

You can also use pipes to pass input to `cortex-shell`:

```shell
cat fizz_buzz.py | cortex-shell -c "Generate comments for each line of my code"
```

```python
# Define the fizz_buzz function with a parameter n
def fizz_buzz(n):
    # Iterate through numbers from 1 to n (inclusive)
    for i in range(1, n+1):
        # Check if the number is divisible by both 3 and 5
        if i % 3 == 0 and i % 5 == 0:
            # Print "FizzBuzz" if the number is divisible by both 3 and 5
            print("FizzBuzz")
        # Check if the number is divisible by 3
        elif i % 3 == 0:
            # Print "Fizz" if the number is divisible by 3
            print("Fizz")
        # Check if the number is divisible by 5
        elif i % 5 == 0:
            # Print "Buzz" if the number is divisible by 5
            print("Buzz")
        # If the number is not divisible by 3 or 5
        else:
            # Print the number itself
            print(i)

# Call the fizz_buzz function with the argument 100
fizz_buzz(100)
```

## Conversational Modes - Overview

Often it is important to preserve and recall a conversation, which is kept track of locally. `cortex-shell` creates conversational dialogues with each LLM completion requested. A persistent dialogue will be initiated or resumed if the option `--id` is used. The histories are located at [config option](#runtime-configuration-file) `chat_history_path`.

### Sessions

To start a chat session, use the `--id` option followed by a unique session name.

```shell
cortex-shell --id number "please remember my favorite number: 4"
# I have stored your favorite number: 4.
cortex-shell --id number "what would be my favorite number + 4?"
# Your favorite number is 4. Adding 4 to it would be 4 + 4 = 8.
```

You can also use chat sessions to iteratively improve GPT suggestions by providing additional clues.

```shell
cortex-shell --id python_request -c "make an example request to localhost using Python"
```

```python
import requests

response = requests.get('http://localhost')
print(response.text)
```

Asking AI to add a cache to our request.

```shell
cortex-shell --id python_request -c "add caching"
```

```python
import requests
from cachetools import cached, TTLCache

cache = TTLCache(maxsize=100, ttl=300)

@cached(cache)
def get_request(url):
    response = requests.get(url)
    return response.text

url = "http://localhost"
response_text = get_request(url)
print(response_text)
```

We can use `--id` with `--code` or `--shell` options, so you can keep refining the results:

```shell
cortex-shell --id sh --shell "What are the files in this directory?"
# ls
cortex-shell --id sh "Sort them by name"
# ls | sort
cortex-shell --id sh "Concatenate them using FFMPEG"
# ffmpeg -i "concat:$(ls | sort | tr '\n' '|')" -codec copy output.mp4
cortex-shell --id sh "Convert the resulting file into an MP3"
# ffmpeg -i output.mp4 -vn -acodec libmp3lame -ac 2 -ab 160k -ar 48000 final_output.mp3
```

### Listing and Showing Chat Sessions

To list all the sessions from either conversational mode, use the `--list-chats` option:

```shell
cortex-shell --list-chats
# /tmp/cortex-shell/history/number.yaml
# /tmp/cortex-shell/history/python_request.yaml
```

To show all the messages related to a specific conversation, use the `--show-chat` option followed by the session name:

```shell
cortex-shell --show-chat number
# system: ...
# user: please remember my favorite number: 4
# assistant: I have stored your favorite number: `4`.
# user: what would be my favorite number + 4?
# assistant: Your favorite number is `4`. Adding `4` to it would be `4 + 4 = 8`.
```

## Request Cache

Control cache using `--cache` (default) and `--no-cache` options. This caching applies to all `cortex-shell` requests to the LLM:

```shell
cortex-shell "what are the colors of a rainbow"
# The colors of a rainbow are red, orange, yellow, green, blue, indigo, and violet.
```

Next time, the same exact query will get results from the local cache instantly. Note that `cortex-shell "what are the colors of a rainbow" --temperature 0.5` will make a new request, since we didn't provide `--temperature` (same applies to `--top-probability`) on the previous request.

This is just some examples of what we can do using OpenAI GPT models. We're sure you'll find it useful for your specific use cases.

## Roles

CortexShell allows you to create custom roles, which can be utilized to generate code, shell commands, or to fulfill your specific needs. Roles can be defined in the config file under the `roles` key. At minimum, you have to define a `name` and a `description`. It's also possible to define model options and/or output options there.

```yaml
# config.yaml
roles:
  - name: pirate
    description: you are a pirate
    options:
      temperature: 0.5
```

```shell
cortex-shell --role pirate hi
# Ahoy matey! Welcome aboard! What can I do for ye today?
```

## Runtime Configuration File

You can set up some parameters in the runtime configuration file `~/.config/cortex-shell/config.yaml`:

```yaml
apis:
  chatgpt:
    api_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx # your api key
    azure_endpoint: https://xxxx.azure.com # this setting is only required if you are accessing ChatGPT via Azure
misc:
  request_timeout: 10
  session:
    chat_history_path: /home/user/.cache/cortex-shell/history
    chat_history_size: 100
    chat_cache_path: /tmp/cortex-shell/cache
    chat_cache_size: 100
    cache: true
default:
  role: # set a new default role. must be defined in "roles"
  options:
    api: chatgpt # only valid option is "chatgpt" currently
    model: gpt-4-1106-preview
    temperature: 0.1
    top_probability: 1.0
  output:
    stream: true
    formatted: true
    color: blue # possible values: black, red, green, yellow, blue, magenta, cyan, gray, brightblack, brightred, brightgreen, brightyellow, brightblue, brightmagenta, brightcyan, white
    theme: dracula # possible values: https://pygments.org/styles/
builtin_roles:
  code:
    options: # all default options can be overriden
  shell:
    options: # all default options can be overriden
    default_execute: false # pre-select "execute" instead of "abort" in shell-mode
  describe_shell:
    options: # all default options can be overriden
roles:
  - name: pirate # role id to be used with --role "id"
    description: you are a pirate # the description of your role
    options: # default values can be overriden
    output: # default values can be overriden
```

## Overriding Config File Parameters with Command-Line Options

CortexShell allows you to override most parameters specified in the configuration file (`~/.config/cortex-shell/config.yaml`) using command-line options. This flexibility enables you to customize CortexShell's behavior for specific tasks without permanently modifying the configuration file.

For example, if you have set a default temperature value in the configuration file, you can override it for a single CortexShell invocation using the `--temperature` option:

```shell
cortex-shell --temperature 0.7 "Generate a creative project idea"
```

This command will generate a creative project idea using a temperature of 0.7, regardless of the default temperature value specified in the configuration file.

Similarly, you can override other parameters, such as `--top-probability`, `--model`, and output options like `--color` and `--theme`. Here's an example that overrides multiple parameters:

```shell
cortex-shell --temperature 0.5 --top-probability 0.9 --color green --theme solarized-dark "Explain the concept of recursion"
```

This command will provide an explanation of recursion using a temperature of 0.5, a top probability of 0.9, and a green-colored output with the Solarized Dark theme.

By using command-line options, you can easily customize CortexShell's behavior on-the-fly, tailoring its output and functionality to suit your specific needs without altering the default settings in the configuration file.

## Full list of arguments

```text
 Usage: cortex-shell [OPTIONS] [PROMPT]

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   prompt      [PROMPT]  Enter the prompt for generating completions.         │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Input Options ──────────────────────────────────────────────────────────────╮
│ --editor  -e            Open the default text editor to provide a prompt.    │
│ --repl    -r            Initiate a REPL (Read-eval-print loop) session.      │
│ --file    -f      FILE  Use one or more files as additional input.           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Model Options ──────────────────────────────────────────────────────────────╮
│ --api                    TEXT                      Select the API to be      │
│                                                    used.                     │
│ --model                  TEXT                      Choose the large language │
│                                                    model to be utilized.     │
│ --temperature            FLOAT RANGE               Adjust the randomness of  │
│                          [0.0<=x<=2.0]             the generated output.     │
│ --top-probability        FLOAT RANGE               Limit the highest         │
│                          [0.0<=x<=1.0]             probable tokens (words).  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Output Options ─────────────────────────────────────────────────────────────╮
│ --stream         --no-stream             Enable or disable stream output.    │
│ --formatted      --no-formatted          Enable or disable formatted output. │
│ --color                            TEXT  Set the output color.               │
│ --theme                            TEXT  Choose the output theme.            │
│ --output     -o                    PATH  Specify a file to store the         │
│                                          assistant's last message.           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Cache Options ──────────────────────────────────────────────────────────────╮
│ --cache          --no-cache      Enable or disable caching of completion     │
│                                  results.                                    │
│ --clear-cache                    Clear the cache.                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Chat Options ───────────────────────────────────────────────────────────────╮
│ --id           -i      TEXT  Start or continue a conversation with a         │
│                              specific chat ID.                               │
│ --show-chat            TEXT  Display all messages from the provided chat ID. │
│ --delete-chat          TEXT  Delete a single chat with the specified ID.     │
│ --list-chats                 List all existing chat IDs.                     │
│ --clear-chats                Delete all chats.                               │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Role Options ───────────────────────────────────────────────────────────────╮
│ --code            -c            Generate code only.                          │
│ --describe-shell  -d            Describe a shell command.                    │
│ --shell           -s            Generate and execute shell commands.         │
│ --role                    TEXT  Define the system role for the large         │
│                                 language model.                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Other Options ──────────────────────────────────────────────────────────────╮
│ --install-integration          Install shell integration (Fish, Bash, ZSH    │
│                                and Powershell supported).                    │
│ --version                      Display the current version.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```
