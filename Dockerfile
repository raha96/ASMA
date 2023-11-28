# Use the official Python image as the base image
FROM python:3.10

# Install build dependencies
RUN apt-get update
RUN apt-get install -y git autoconf gperf make gcc g++ bison flex

WORKDIR /iverilog

# Install iverilog
RUN git clone https://github.com/steveicarus/iverilog
WORKDIR /iverilog/iverilog
RUN sh autoconf.sh
RUN ./configure
RUN make
RUN make install

# Check that iverilog is installed
RUN iverilog -V

#######################################

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 80 for Streamlit
EXPOSE 80

# Command to run on container start
CMD ["streamlit", "run", "asma_streamlit_app.py", "--server.port", "80"]
