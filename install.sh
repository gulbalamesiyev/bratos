#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  BRATOS INSTALLER v1.5
#  Azərbaycanın ilk Hacking Əməliyyat Sistemi
#  Developer: Masiyev Gülbala
# ═══════════════════════════════════════════════════════════

clear

RED='\033[1;31m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
WHITE='\033[1;37m'
YELLOW='\033[1;33m'
RESET='\033[0m'

echo ""
echo -e "${RED}╔═══════════════════════════════════════════════════════════╗"
echo -e "${RED}║                                                           ║"
echo -e "${RED}║    ${GREEN}██████╗ ██████╗  █████╗ ████████╗ ██████╗ ███████╗${RED}     ║"
echo -e "${RED}║    ${GREEN}██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝${RED}     ║"
echo -e "${RED}║    ${GREEN}██████╔╝██████╔╝███████║   ██║   ██║   ██║███████╗${RED}     ║"
echo -e "${RED}║    ${GREEN}██╔══██╗██╔══██╗██╔══██║   ██║   ██║   ██║╚════██║${RED}     ║"
echo -e "${RED}║    ${GREEN}██████╔╝██║  ██║██║  ██║   ██║   ╚██████╔╝███████║${RED}     ║"
echo -e "${RED}║    ${GREEN}╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝${RED}     ║"
echo -e "${RED}║                                                           ║"
echo -e "${RED}║    ${WHITE}Azərbaycanın ilk Hacking Əməliyyat Sistemi${RED}             ║"
echo -e "${RED}║    ${CYAN}Developed by: ${WHITE}Masiyev Gülbala${RED}                          ║"
echo -e "${RED}║                                                           ║"
echo -e "${RED}╚═══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}[*] BratOS quraşdırılır...${RESET}"
echo ""

# ═══════════════ 1. Tələblər ═══════════════
echo -e "${BLUE}[1/6]${RESET} Tələblər yoxlanır..."

if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}[!] BratOS yalnız Termux-da işləyir!${RESET}"
    exit 1
fi

echo -e "${YELLOW}      Paketlər quraşdırılır...${RESET}"
pkg update -y > /dev/null 2>&1
pkg install -y python git wget curl fish > /dev/null 2>&1

echo -e "${GREEN}      ✓ Tələblər hazırdır${RESET}"

# ═══════════════ 2. Qovluqlar ═══════════════
echo -e "${BLUE}[2/6]${RESET} BratOS sistemi qurulur..."
mkdir -p ~/.bratos/{tools,bin,cache}

# ═══════════════ 3. BratOS Core ═══════════════
echo -e "${BLUE}[3/6]${RESET} BratOS Core yüklənir..."

curl -fsSL https://raw.githubusercontent.com/gulbalamesiyev/bratos/main/brat.py -o ~/.bratos/brat 2>/dev/null

chmod +x ~/.bratos/brat
ln -sf ~/.bratos/brat ~/.bratos/bin/brat

echo -e "${GREEN}      ✓ BratOS Core hazırdır${RESET}"

# ═══════════════ 4. Banner ═══════════════
echo -e "${BLUE}[4/6]${RESET} Banner quraşdırılır..."

cat > ~/.bratos/banner.sh << 'BANNER'
#!/bin/bash
clear
RED='\033[1;31m'
DRED='\033[38;5;88m'
WHITE='\033[1;37m'
GRAY='\033[38;5;245m'
CYAN='\033[1;36m'
RESET='\033[0m'
echo ""
echo -e "${RED}    ╔═══════════════════════════════════════════════════════════╗"
echo -e "${RED}    ║                                                           ║"
echo -e "${RED}    ║    ${DRED}██████╗ ██████╗  █████╗ ████████╗ ██████╗ ███████╗${RED}     ║"
echo -e "${RED}    ║    ${DRED}██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝${RED}     ║"
echo -e "${RED}    ║    ${DRED}██████╔╝██████╔╝███████║   ██║   ██║   ██║███████╗${RED}     ║"
echo -e "${RED}    ║    ${DRED}██╔══██╗██╔══██╗██╔══██║   ██║   ██║   ██║╚════██║${RED}     ║"
echo -e "${RED}    ║    ${DRED}██████╔╝██║  ██║██║  ██║   ██║   ╚██████╔╝███████║${RED}     ║"
echo -e "${RED}    ║    ${DRED}╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝${RED}     ║"
echo -e "${RED}    ║                                                           ║"
echo -e "${RED}    ║    ${WHITE}Azərbaycanın ilk Hacking Əməliyyat Sistemi${RED}             ║"
echo -e "${RED}    ║    ${CYAN}Developed by: ${WHITE}Masiyev Gülbala${RED}                          ║"
echo -e "${RED}    ║    ${GRAY}github.com/gulbalamesiyev/bratos-tools${RED}                 ║"
echo -e "${RED}    ║                                                           ║"
echo -e "${RED}    ╚═══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${RESET}"
BANNER

chmod +x ~/.bratos/banner.sh
echo -e "${GREEN}      ✓ Banner quraşdırıldı${RESET}"

# ═══════════════ 5. Fish Shell ═══════════════
echo -e "${BLUE}[5/6]${RESET} Fish Shell konfiqurasiya edilir..."
mkdir -p ~/.config/fish

cat > ~/.config/fish/config.fish << 'FISH'
set -gx PATH $HOME/.bratos/bin $PATH

function brat
    python3 ~/.bratos/brat $argv
end

function doctor
    python3 ~/.bratos/brat doctor
end

function clear
    printf "\033[2J\033[H"
    bash ~/.bratos/banner.sh
end

function fish_greeting
    bash ~/.bratos/banner.sh
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
FISH

echo -e "${GREEN}      ✓ Fish Shell hazırdır${RESET}"

# ═══════════════ 6. Repo ═══════════════
echo -e "${BLUE}[6/6]${RESET} Alət reponu klonlanır..."

if [ -d ~/bratos-tools ]; then
    echo -e "${YELLOW}      Repo mövcuddur, yenilənir...${RESET}"
    cd ~/bratos-tools && git pull > /dev/null 2>&1
else
    git clone https://github.com/gulbalamesiyev/bratos-tools.git ~/bratos-tools > /dev/null 2>&1
fi

echo -e "${GREEN}      ✓ Repo hazırdır${RESET}"

# ═══════════════ ALIAS ═══════════════
# Alias-ları .bashrc-ə əlavə et
if ! grep -q "alias bratos=" ~/.bashrc 2>/dev/null; then
    echo 'alias bratos="fish"' >> ~/.bashrc
fi
if ! grep -q "alias brat=" ~/.bashrc 2>/dev/null; then
    echo 'alias brat="python3 ~/.bratos/brat"' >> ~/.bashrc
fi

# PATH əlavə et
if ! grep -q "bratos/bin" ~/.bashrc 2>/dev/null; then
    echo 'export PATH="$HOME/.bratos/bin:$PATH"' >> ~/.bashrc
fi

# ═══════════════ BİTDİ ═══════════════
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗"
echo -e "${GREEN}║                                                           ║"
echo -e "${GREEN}║         Quraşdırma tamamlandı! 🎉                          ║"
echo -e "${GREEN}║                                                           ║"
echo -e "${GREEN}║    Əmrlər:                                                ║"
echo -e "${GREEN}║    ${WHITE}bratos${GREEN}        - BratOS terminalını başlat          ║"
echo -e "${GREEN}║    ${WHITE}brat help${GREEN}    - Bütün əmrləri göstər              ║"
echo -e "${GREEN}║    ${WHITE}brat update${GREEN}  - Paket indeksini yenilə            ║"
echo -e "${GREEN}║    ${WHITE}brat browse${GREEN}  - İnteraktiv alət menyusu          ║"
echo -e "${GREEN}║                                                           ║"
echo -e "${GREEN}║    ${YELLOW}Terminalı bağlayıb yenidən açın...${GREEN}                   ║"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝"
echo ""
