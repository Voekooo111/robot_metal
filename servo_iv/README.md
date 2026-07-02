## Установка зависимостей

``` bash
sudo apt update
sudo apt install swig python-dev python3-dev python-setuptools python3-setuptools
sudo apt install python3-lgpio
pip install flask
```

### Сервер raspberry
Проверка
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

---
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-enabled/default
```
```
location / {
    proxy_pass http://127.0.0.1:5000;

    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```