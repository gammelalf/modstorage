function __get_mods
	modstorage --list-mods
end

function __get_packs
	modstorage --list-packs
end

complete -c modstorage -l help -s h -d "Show help message and exit"
complete -c modstorage -l version    -x
complete -c modstorage -l mod        -x -a "(__get_mods)"
complete -c modstorage -l pack       -r -a "(__get_packs)"

complete -c modstorage -l new-mod    -r -d "Create new mod"
complete -c modstorage -l add-file   -r -d "Add a jar file"
complete -c modstorage -l add-dependencies -x -a "(__get_mods)"
complete -c modstorage -l read          -d "Experimental! Read the mcmod.info"

complete -c modstorage -l new-pack   -r -d "Create new pack"
complete -c modstorage -l add           -d "Add a mod to a pack"
complete -c modstorage -l remove        -d "Remove a mod from a pack"
complete -c modstorage -l autoremove    -d "See apt's autoremove"
complete -c modstorage -l list          -d "List mods"
