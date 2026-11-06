#!/bin/bash

# Uso: hook_writer.sh Nombre_del_Hook directorio repositorio_git

cat << EOF > $1
#!/bin/bash
mkdir -p $2 2>/dev/null
git clone $3 $2
EOF
