if pipx list | grep -q "package splitter"; then
    read -r -p "A previous installation of splitter exists and will be removed. Do you wish to continue? [y/n]: " answer

    if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
        echo "Installation cancelled."
        exit 0
    fi

    pipx uninstall splitter 2>/dev/null 1>/dev/null
fi

pipx install .

