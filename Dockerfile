FROM ubuntu:22.04

WORKDIR /app

COPY . .

RUN apt update && apt install python3 python3-pip git -y
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r ./requirements.txt
RUN pip3 install python-dotenv

# TODO: Implement execution of user python code
COPY examples/fast_food/fast_food.py fast_food.py
CMD python3 fast_food.py
