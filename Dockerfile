# this is an official Python runtime, used as the parent image
FROM python:3.8-slim-buster

# set the working directory in the container to /app
WORKDIR /app

# add the current directory to the container as /app
ADD . /app

COPY requirements.txt requirements.txt

# execute everyone's favorite pip command, pip install -r
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

COPY . .

# unblock port 80 for the Flask app to run on
#EXPOSE 80
EXPOSE 5002

# execute the Flask app
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5002"]