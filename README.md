<h1 align="center"> 
    🔥 API 🔥
</h1>



</br>



<h2>
  💾 DTOs
</h2>

<h3>
  В этом разделе собраны все Data Transfer Objects проекта
</h3>

<br/>
<hr/>

<h3>
    
`user_dto`

</h3>
<h4>
    Объект пользователя
</h4>

<br/>

```
{
    username: string,
    email: string,
}
```


<br/>
<hr/>


<br/>
<br/>
<br/>



<h2>
  📁 FILES API
</h2>

<h3>
  URL-шаблон указывающий на файл urls.py внутри приложения 'src.convert', который содержит дополнительные URL-шаблоны, для функциональности работы с файлами
</h3>


<br/>
<hr/>


<h3>


    
🟠 POST `api_url/file/upload/`

</h3>
 
<h4>
    Загрузка файла на сервер и дальнейшая его обработка
</h4>

<br/>

Headers:

```
{
    Cookie: token="your_token"
    Authorization: Bearer "your_token"
}
```

<br/>

Response:

```
{
    "file_url": url 
    Cookie: token="your_token",
    Authorization: Bearer "your_token",
}
```

<br/>

Requset:

```
{
    file_path: [Binary data of the file],
    to: str (Выходной формат файла),
    id: int (Идентификатор пользователя),
}
```

<br/>

Response:
```
{
    file_url: string (ссылка на скачивание файла),
}
```

<br/>
<hr/>


<h3>

    
🟢 GET `api_url/file/download/int:file_id/`
    
</h3>
<h4>
   Скачивание файла для авторизованных пользователей
</h4>

<br/>

Headers:

```
{
    Cookie: token="your_token"
    Authorization: Bearer "your_token"
}
```

<br/>

Response:

```
{
    HTTP/1.1 200 OK
    Content-Type: application/octet-stream
    Content-Disposition: attachment; filename="your_filename"
    
    [Binary data of the file]
    Cookie: token="your_token",
    Authorization: Bearer "your_token",
}
```

<br/>

Requset:

```
{
    pk: int  (Идентификатор файла, который требуется скачать),
}
```

<br/>

> Должна возвращаться ссылка на файл
> 
Response:
```
{
    file_url: string (ссылка на скачивание файла),
}
```

<br/>
<hr/>


<h3>

    
🔴 DELETE `api_url/file/delete/int:pk/`

</h3>

<h4>
    Удаление файла для авторизованных пользователей
</h4>

<br/>

Headers:

```
{
    Cookie: token="your_token"
    Authorization: Bearer "your_token"
}
```

<br/>

Response:

```
{
    "Файл успешно удален"
    HTTP/1.1 204 No Content
    
    Cookie: token="your_token",
    Authorization: Bearer "your_token",

}
```

<br/>

Requset:

```
{    
    pk: int  (Идентификатор файла, который требуется удалить),
}
```


<br/>

> Должно возвращаться сообщение об удачном или неудачном удалении
> 
Response:
```
{
    message: string,
}
```

<br/>
<hr/>



<br/>
</br>
<br/>



<h2>
   👴 USERS API
</h2>

<h3>
  URL-шаблон указывающий на файл urls.py внутри приложения 'src.oauth', который содержит пути к представлениям для регистрации, входа, обновления профиля пользователя и другим функциям, связанным с учетными записями пользователей
</h3>


<br/>
<hr/>


<h3>
    
🟣 PATCH `api_url/user/update/`

</h3>
<h4>
    Отвечает за обновление информации о пользователе. При обращении к этому URL пользователь может изменять свои данные или профиль
</h4>
<br/>

Headers:

```
{
    Cookie: token="your_token"
    Authorization: Bearer "your_token"
}
```

<br/>

Response:

```
{
    "username": str (Измененное имя),
    "email": str (Измененный Email)

    Cookie: token="your_token",
    Authorization: Bearer "your_token",
}
```

<br/>

Requset:

```
{
    user: {
        username: string (Имя пользователя),
        email: string (Email пользователя),
    }
}
```

<br/>

Response:
```
{
    username: string (Измененное имя),
    email: string (Измененный Email),
}
```


<br/>
<hr/>


<h3>
    
🟠 POST `api_url/user/register/`

</h3>
<h4>
    Обрабатывает процесс регистрации новых пользователей
</h4>


<br/>



Requset:

```
{
    user: {
        username: string,
        email: string,
        password: string,
    }
}
```

<br/>



Response:

```
{
    access_token: "your_acces_token",
    user: user_dto,
}
```

<br/>
<hr/>


<h3>
    
🟠 POST `api_url/user/login/`

</h3>
<h4>
    Отвечает за аутентификацию пользователей. При обращении к этому URL пользователи могут войти в систему, предоставив свои учетные данные (имя пользователя и пароль)
</h4>

<br/>

Requset:
```
{
    user: {
        username: string, 
        password: string,
    }
}
```

<br/>

Response:
```
{
    access_token: "your_acces_token",
    user: user_dto,
}
```

<br/>
<hr/>

<h3>
    api_url/user/logout/
</h3>
<h4>
    Отвечает за выход пользователя из системы.
</h4>

<br/>


Response:

```
{
    "detail": "Вы успешно вышли из системы."
    HTTP/1.1 200 OK
}
```

<br/>

Requset:

```
{
    Cookie: token="your_token"
    Authorization: Bearer "your_token"
}
```

<br/>
<hr/>


<h3>
    
🟢 GET `api_url/user/token/refresh/`

</h3>  
<h4>
    Обрабатывает запросы на обновление токена аутентификации. При обращении к этому URL пользователь может запросить обновление токена для продления срока его действия
</h4>

<br/>

Headers:

```
{
    Cookie: token="your_token" (никакие действия с куками на фронте не нужно делать),
}
```

<br/>

Response:

```
{
    access_token: "your_acces_token",
    user: user_dto,
}
```

<br/>
<hr/>


<h3>
    
🟠 POST `api_url/user/password/reset/`
    
</h3>
<h4>
    Обрабатывает запросы на сброс пароля и отправляет соответствующую информацию по электронной почте
</h4>



<br/>

Response:

```
{
    url: ссылка для сброса пароля
}
```

<br/>

Requset:

```
{
    email: string (Email на который будет отправленна ссылка для сброса),
}
```

<br/>

Response:
```
{
    url: string (ссылка для сброса пароля),
}
```

<br/>
<hr/>


<h3>
    
🟠 POST `api_url/user/password/reset/confirm///`

</h3>
<h4>
    Отвечает за подтверждение сброса пароля после получения уникального идентификатора uidb64 и токена token
</h4>

<br/>


Requset:
```
{
    new_password: string,
    confirm_password: string,
}
```

<br/>

Response:
```
{
    detail: "Пароль был сброшен",
    HTTP/1.1 200 OK
}
```

<br/>
<hr/>






<br/>
<br/>
<br/>
<br/>
<br/>





<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=dd6ee0&height=80&section=footer"/>
</p>
