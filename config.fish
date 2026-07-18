set -gx PATH $HOME/.bratos/bin $PATH

function brat
    python3 ~/.bratos/brat $argv
end

function doctor
    python3 ~/.bratos/brat doctor
end

function fish_greeting
    bash ~/.bratos/banner.sh
end

# clear override - banneri qoruyur
function clear
    printf "\033[2J\033[H"  # Ekranı təmizlə
    bash ~/.bratos/banner.sh  # Banneri yenidən göstər
end

function fish_prompt
    set_color blue
    echo -n "╭─"
    set_color red
    echo -n "root"
    set_color white
    echo -n "@"
    set_color blue
    echo -n "bratos "
    set_color cyan
    echo -n "["(prompt_pwd)"]"
    set_color blue
    echo -n " ["
    set_color green
    echo -n (date +%H:%M:%S)
    set_color blue
    echo "]"
    echo ""
    set_color blue
    echo -n "╰─"
    set_color red
    echo -n "➤ "
    set_color normal
end

set -g fish_history ~/.bratos/fish_history
