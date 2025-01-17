from run import Terminal

terminal = Terminal()
shell = terminal.create_shell()
shell.run_command("ls")
print(terminal)
