#Reload the completions for testing
#To use just source this file

fpath=($PWD $fpath)
unfunction _cromshell
autoload -U compinit
compinit
