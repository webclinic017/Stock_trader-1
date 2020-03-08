from app import app

# Usage: gunicorn --workers=4 --threads=8 --bind 0.0.0.0:5000 driver_webserver:app [workers|threads = 2-4 * num_cores]

def main():
    # For development
    app.run(debug=True, host='0.0.0.0')

    # For deployment
    # app.run("0.0.0.0", "5000")


if __name__ == '__main__':
    main()
