# Reload the _cromshell completion file for testing
# Usage:
# source reload.sh

fpath=($PWD $fpath)
unfunction _cromshell
autoload -U compinit
compinit
