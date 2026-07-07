# Robot_metal

## Установка зависимостей

``` bash
sudo apt update
sudo apt upgrade -y
sudo apt install nginx -y
```

### Сервер raspberry
#### Проверка nginx
```bash
sudo systemctl status nginx
```

#### Проверка avahi-daemon
```bash
sudo systemctl status avahi-daemon
```
Если нет, то:
```bash
sudo apt update
sudo apt install avahi-daemon
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```
---
```bash
hostname
```
http://\<hostname\>.local - подключение к raspberry.
И проерим, что появится Welcome to nginx!
---
#### venv
```bash
sudo apt install python3 python3-venv python3-pip -y
sudo apt install python3-lgpio -y
python3 -m venv --system-site-packages venv
source venv/bin/activate
```
Зависимости.
```bash
pip install flask
```

```bash
sudo nano /etc/nginx/sites-available/servo_iv
```
```
server {

    listen 80;

    server_name <hostname>.local _;

    location / {

        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

    }

}
```

```bash
sudo ln -s /etc/nginx/sites-available/servo_iv /etc/nginx/sites-enabled/
```
Если ссылка уже существует
```bash
sudo rm /etc/nginx/sites-enabled/servo_iv
sudo ln -s /etc/nginx/sites-available/servo_iv /etc/nginx/sites-enabled/
```
```bash
sudo rm /etc/nginx/sites-enabled/default
```
#### Проверка конфигурации
```bash
sudo nginx -t
```
```bash
sudo systemctl restart nginx
```

```bash
sudo nano /etc/systemd/system/robot_metal.service
```

```
[Unit]
Description=Robot Metal
After=network.target

[Service]
User=user
WorkingDirectory=/home/user/robot_metal
Environment="PATH=/home/user/robot_metal/venv/bin"
ExecStart=/home/user/robot_metal/venv/bin/python /home/user/robot_metal/robot_metal.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable robot_metal
sudo systemctl start robot_metal
```
Проверка
```bash
sudo systemctl status robot_metal
```

#### Доп-команды
```bash
sudo systemctl restart robot_metal
```
Терминал для Flask
```bash
journalctl -u robot_metal -f
```
Nginx
```bash
sudo systemctl restart nginx
sudo nginx -t
```
