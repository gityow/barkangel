FROM centos:7

# Install Java
RUN yum update -y \
&& yum install java-1.8.0-openjdk -y \
&& yum clean all \
&& rm -rf /var/cache/yum

# Set JAVA_HOME environment var
ENV JAVA_HOME="/usr/lib/jvm/jre-openjdk"

# Install Python
RUN yum install python3 -y \
&& pip3 install --upgrade pip setuptools wheel \
&& if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
&& if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
&& yum clean all \
&& rm -rf /var/cache/yum

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

### 4. COPY . /app
COPY . /app

EXPOSE 8080
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8080"]