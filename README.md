`aws --endpoint-url=http://localhost:4566 s3 cp test-video.mp4 s3://test-bucket/test-video.mp4`

Pra rodar localmente precisa iniciar o docker-compose com:
```docker compose up --build```

Pra testar a função lambda no localstack

```cd src```
```sudo zip ../localstack/init/lambda/lambda.zip app.py utils.py```

Precisa adicionar a imagem no bucket:
```aws --endpoint-url=http://localhost:4566 s3 cp test-video.mp4 s3://test-bucket-in/video2.mp4```

```aws --endpoint-url=http://localhost:4566 s3 cp test-gif.gif s3://test-bucket-in/gif-test.gif```