# Deployment Manuel (Paradigm Layout)

## Prerequisites

1. Install python3 (for your us) (make sure version > 3.8.2)
2. ```pip install pip install "fastapi[all]" ```
3.  Install ```nvm``` use [this tutorial](https://github.com/nvm-sh/nvm)
4.  Install node using nvm. Same Tutorial as 3
5. `git clone {our repo}`

### Note:
All version for ```npm``` should be the latest. 


## Test Webserver Security Curtin

First we need to set `screen` so cybera doesn't kill the process when we exit the server. 

`screen -S internet_facing`

Second things second we use fast api to run the test development server. This means that we need to install it:

`pip install "uvicorn[standard]"`

Next things next we need to make a run file that will talk to the `localhost` i.e the backend that should **never** be exposed to the internet without filtering. This means to do the following:

`mkdir internet_facing`

`cp -r main.py .../internet_facing` 

Assuming fast api and uvicorn are installed together run the following command. 

`uvicorn main:app --port 8081` 

Assuming everything ran without issues do the following:

`ctrl-a d`

## Frontend Deployment

Follow these steps exactly as failure to this will cause the system to not render properly. 

### Website 
1. `cd morphodict` From the current repo page.
2. `rm package-lock.json`
3. `npm i` 
4. `npm run build` 
5. `cd build`
6. `pwd`
7. Copy the results from 7

After runnin this the website should build correctly.
### Server 
1. `sudo apt-get install nginx`
2. `cd /etc/nginx/sites-available/`
3. `sudo nano morph_deploy.nginx`
4. Paste the following:

{

    server 
        {
            
            listen 80;
            
            root {#8 pasted from above};
            index index.html;

            location / {
            try_files $uri /index.html;
            }

            location /local/ {
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_redirect off;
            proxy_buffering off;
            proxy_pass http://127.0.0.1:8081;
            }
        }

    server {

        listen [::]:80;

        root {#8 pasted from above};;
        index index.html;

        location / {
            try_files $uri /index.html;
        }

        location /local/ {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_redirect off;
        proxy_buffering off;
        proxy_pass http://[::1]:8081;
        }

        }
}

5. `sudo ln -s /etc/nginx/sites-available/morph_deploy.nginx /etc/nginx/sites-enabled/morph_deploy.nginx`

6. `sudo nginx -T` Confirm no erros are encountered
7. `sudo systemctl reload nginx`

From here you should be done, now time to launch the database!

## Backend REST API

Please follow along from here: https://morphodict.readthedocs.io/en/latest/developers-guide.html#installing-for-the-first-time
