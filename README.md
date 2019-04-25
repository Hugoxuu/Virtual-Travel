# Virtual-Travel
It is a website that provides user with virtual travel experience. [Visit our website](http://100.24.61.190)!

## About the project
We are a team of four (Lijuan Shen, Yan Pan, Yi He, Zeyuan Xu). <br>
This project is under the instruction of Prof. Jeff Eppinger and TAs from CMU-17437-SP19.

## Tools
1. Django Web Framework, Bootstrap
2. Python, Javascript, HTML, CSS
3. Google Maps API, Yelp API

## How to Set Up? (On Linux or mac Terminal)
1. Make sure you have django and python installed:
    ```
    $ sudo apt-get update;
    $ sudo apt-get install python3-pip;
    $ sudo -H pip3 install --upgrade pip;
    $ sudo -H pip3 install django==2.1.5;
    $ sudo reboot;
    ```
2. To run the website on your computer:
    ```
    $ git clone https://github.com/Hugoxuu/Virtual-Travel;
    $ cd Virtual-Travel/;
    $ ./dbinit.sh python3;
    $ python3 manage.py runserver;

## How to Set Up? (On Linux & mac Terminal)
1. Make sure you have django and python installed:
    ```
    $ sudo apt-get update
    $ sudo apt-get install python3-pip
    $ sudo -H pip3 install --upgrade pip
    $ sudo -H pip3 install django==2.1.5
    $ sudo reboot
    ```
2. To setup the website server on your computer:
    ```
    $ git clone https://github.com/Hugoxuu/Virtual-Travel;
    $ cd Virtual-Travel/;
    $ ./dbinit.sh python3; # [python3] - your python version
    ```
3. Browser:
    ```
    http://127.0.0.1:8000/
    ```
### References
1. *[Google My Maps API](https://www.google.com/earth/outreach/learn/visualize-your-data-on-a-custom-map-using-google-my-maps/#embed_your_map)
2. *[Yelp API, yelp.py](https://www.yelp.com/developers/documentation/v3)
3. *[Django](https://www.djangoproject.com/)
4. *[Bootstrap 4](https://getbootstrap.com/)
5. *[jQuery](https://jquery.com/)
6. *[Background Canvas Effect](https://github.com/sunshine940326/canvas-nest)
