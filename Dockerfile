# Dockerfile, Image, Container
FROM python:3.9.5

# ADD Script, Folder
ADD run.py .

# Install packages 
RUN pip install flask_sqlalchemy flask pandas openpyxl

# How to run it
CMD ["python", "./run.py"]