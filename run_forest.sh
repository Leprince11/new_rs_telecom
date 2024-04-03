# Provides:          my-service-name
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: your description here
### END INIT INFO

# Activer l'environnement virtuel sans utiliser 'source'
VENV_DIR="/home/ubuntu/new_rs_telecom/venv"
if [ -d "$VENV_DIR" ]; then
    . "$VENV_DIR/bin/activate"
else
    echo "Virtual environment directory not found: $VENV_DIR"
    exit 1
fi

# Utiliser le Python de l'environnement virtuel
PYTHON="$VENV_DIR/bin/python3"

# Assurez-vous que le chemin vers votre script manage.py est correct
MANAGE_SCRIPT="/home/ubuntu/new_rs_telecom/manage.py"

# Exécutez votre script Python
$PYTHON $MANAGE_SCRIPT runserver
