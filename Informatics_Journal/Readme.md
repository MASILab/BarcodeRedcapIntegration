
# build docker :
#### sudo docker build -t info_app3 -f Dockerfile_test .

# run docker  (for example, if try to run location app v1) : 
#### sudo docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix info_app3 python /app/v1/LocationApp_v1/main.py
