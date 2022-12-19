# ДЗ-2
## 1. Используемые сервисные аккаунты
### face-detection-function:
- ai.vision.user
- ymq.writer
- storage.viewer  
### function-invoker:
- serverless.function.invoker  
### face-cut-container:
- storage.viewer
- storage.uploader
- ydb.editor
- container-registry.images.puller  
### face-cut-invoker:
- ymq.reader
- serverless.containers.invoker  
### api-gateway:
- storage.viewer  
### boot-function:
- ydb.viewer
- ydb.editor
## 2. Объекты
### Бакеты
- itis-2022-2023-vvot01-photos
- itis-2022-2023-vvot01-faces
### БД
- vvot01-db-photo-face
### Очереди
- vvot01-tasks
### Триггеры
- vvot01-photo-trigger (сервисный аакаунт **function-invoker**)
- vvot01-task-trigger (сервисный аккаунт **face-cut-invoker**)
### Функции
- vvot01-face-detection (сервисный аккаунт **face-detection-function**, код из файла **functions/PhotoFunction.py**)
- vvot01-boot (сервисный аккаунт **boot-function**, код из файла **functions/BootFunction.py**)
### Контейнер
- vvot01-face-cut (сервисный аккаунт **face-cut-container**, код из папки **container**)
