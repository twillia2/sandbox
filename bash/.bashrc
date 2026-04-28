#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'

# Colours
GREEN='\[\e[32m\]'
BLUE='\[\e[34m\]'
RESET='\[\e[0m\]'

# https://github.com/romkatv/gitstatus
source ~/src/gitstatus/gitstatus.prompt.sh

# https://github.com/trapd00r/LS_COLORS
PS1="\t [${GREEN}\u@\h${RESET} ${BLUE}\w${RESET}]\${GITSTATUS_PROMPT}\$ "
. /usr/share/LS_COLORS/dircolors.sh
