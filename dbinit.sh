if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <your_python3_command>" >&2
  exit 1
fi
PYTHON="$1"
rm db.sqlite3;

$PYTHON manage.py makemigrations;
$PYTHON manage.py migrate;
$PYTHON manage.py shell < dbinit.py;
$PYTHON manage.py runserver;
