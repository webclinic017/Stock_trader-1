from app import app


if __name__ == '__main__':
    # For development
    app.run(debug=True, host='0.0.0.0')

    # For deployment
    # app.run("0.0.0.0", "5000")
