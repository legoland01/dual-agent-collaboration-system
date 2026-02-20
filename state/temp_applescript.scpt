tell application "iTerm2"
    activate
    delay 0.3
    tell first window
        tell current session
            set cmd to "查看TODO" & ASCII character 13
            write text cmd
        end tell
    end tell
end tell