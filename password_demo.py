import termios, sys, tty, select, time

if __name__ == '__main__':
    # Save the terminal setting:
    old_attr = termios.tcgetattr(sys.stdin)

    tty.setcbreak(sys.stdin.fileno())
    password = ''
    sys.stdout.write('Please enter password > ')
    sys.stdout.flush()
    while True:
        if select.select([sys.stdin], [], [], 0)[0] == [sys.stdin]:
            key = sys.stdin.read(1)
            if key == '\n':
                print('\nYou typed: {}'.format(password))
                break
            password += key
            sys.stdout.write('*')
            sys.stdout.flush()
        time.sleep(0.1)

    # Restore the terminal settings, otherwise the terminal will not
    # responding:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_attr)
