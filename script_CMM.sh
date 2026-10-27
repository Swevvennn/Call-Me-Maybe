#!/bin/bash

# Version 1.0.2

CMM_DIR="CMM"
VENV_DIR=venv_CMM
CACHE_DIR="cache_CMM"

CMM_LOCATION="/goinfre/$USER/$CMM_DIR"

export HF_HOME="$CMM_LOCATION/$CACHE_DIR"
export PATH="$PATH:~/.local/bin"

# --- ARGUMENTS CHECK ---
if [ "$1" = "reset" ]; then
	rm -rf ".venv"
	rm -rf "$CMM_LOCATION/$VENV_DIR"
	rm -rf "$CMM_LOCATION/$CACHE_DIR"
elif [ "$1" = "start" ] || [ "$(env | grep VIRTUAL_ENV_PROMPT | cut -b20-99999)" = "$VENV_DIR" ]; then
	if [ "$CACHE_DIR" == $(ls $CMM_LOCATION | grep $CACHE_DIR) && "" != $(ls $CMM_LOCATION | grep "activate") ]; then
		source ./.venv/bin/activate
		printf "\x1b[32mLaunching project !\x1b[0m\n"
		uv --cache-dir "$CMM_LOCATION/$CACHE_DIR" --project llm_sdk run --active python3 -m src
		deactivate
		exit 0
	printf "\x1b[32m[!] Cache folder is missing\x1b[0m\n"
	fi
elif [ "$1" = "help" ]; then
	printf "Usage : bash $0 {start/reset}\n"
	printf "\tstart: Start LLM without passing throught pip and uv check\n"
	printf "\treset: Delete and recreate caching dir\n"
	exit 0
fi

# --- CREATING CACHE DIRECTORY ---
mkdir -p "$CMM_LOCATION/$CACHE_DIR"

# --- INSTALLING UV ---
if [ "$(pip list | grep uv | awk '{print $1}' | head -1)" != "uv" ]; then
	printf "\x1b[32mInstalling uv\x1b[0m\n"
	pip install --user uv
	if [ "$(pip list | grep uv | awk '{print $1}' | head -1)" != "uv" ]; then
		printf "\x1b[32m[!] Failed to installing uv\x1b[0m\n"
		deactivate
		exit 1
	fi
fi

# --- CREATING VENV IF IS NEEDED ---
if [ "$VENV_DIR" != "$(ls "$CMM_LOCATION" | grep "$VENV_DIR")" ]; then
	printf "\x1b[32m[+] Creating venv\x1b[0m\n"
	rm -rf ./.venv/
	rm -rf ./.venv
	uv venv "$CMM_LOCATION/$VENV_DIR"
	ln -s "$CMM_LOCATION/$VENV_DIR" ./.venv
fi
if [ ! -d ".venv" ]; then
	ln -s "$CMM_LOCATION/$VENV_DIR" ./.venv
fi

# --- ACTIVATING VENV IF IS NEEDED ---
if [ "$(env | grep VIRTUAL_ENV_PROMPT | cut -b20-99999)" != "$VENV_DIR" ]; then
	source ./.venv/bin/activate
	if [ $? != 0 ]; then
		printf "\e[0;31m[!] Failed to go into virtual env, try to launch with : \"bash $0 reset\"\e[0m\n"
		exit 1
	fi
fi

# --- INSTALLING UV DEPENDANCY ---
if [ "$(~/.local/bin/uv pip list | grep pydantic | awk '{print $1}' | head -1)" != "pydantic" ]; then
	printf "\x1b[32mInstalling pydantic\x1b[0m\n"
	uv pip install --cache-dir "$CMM_LOCATION/$CACHE_DIR" pydantic
fi
if [ "$(~/.local/bin/uv pip list | grep accelerate | awk '{print $1}' | head -1)" != "accelerate" ]; then
	printf "\x1b[32mInstalling accelerate\x1b[0m\n"
	uv pip install --cache-dir "$CMM_LOCATION/$CACHE_DIR" accelerate
fi

# --- LAUNCHING ---
printf "\x1b[32mLaunching project !\x1b[0m\n"
uv --cache-dir "$CMM_LOCATION/$CACHE_DIR" --project llm_sdk run --active python3 -m src
# Il faut mettre le nom du dossier ou se trouve le main ici.																			
# Si il y a un probleme dm nclavel sur slack ou musashiwithoutkatana sur discord


deactivate
