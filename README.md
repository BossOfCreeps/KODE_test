## Docker  
Build:  
``docker build -t kode .``  
Run:  
``docker run -d -p 8000:80 -v /media:/media kode``  

## Alembic  
Init:  
``alembic init alembic``  
Create migrations "by hands"  
``alembic revision -m "COMMENT"``  
Autogenerated migrations  
``alembic revision --autogenerate -m "COMMENT"``  
Run migrations  
``alembic upgrade head``  

## Pytest
Run:  
``pytest tests --disable-warnings``  

## Сопроводительный текст
### О задании
Не буду скрывать, я не очень хорошо разбираюсь в FastAPI, но хочу научиться. Моим основным фреймворком является Django. Поэтому местами пытался использовать паттерн MVT.  
Отмечу, что опыт работы на другом фреймворке даёт некоторую встряску. Так что в любом случае не жалею что сделал это тестовое задание. Отмечу интересные моменты:

* Я так привык, что в Django "батарейки в комплекте", что и жизни не мог представить без тестов и миграций. Да ладно без миграций - без ORM.
* Продолжая тему. Многое нужно было написать самостоятельно, не жалуюсь, но просто непривычно (ну или просто не нашёл). В частности сериализаторы (для некоторых ситуаций подходят стандартные, но для вывода зависимых моделей (один-к-многим) пришлось писать самостоятельно) и токены для авторизации.
* Из-за того, что много нет, начинаешь ценить то, что есть. Как же мне понравились схемы. Не знаю есть ли такое в DRF, но обязательно поищу и если есть, то буду использовать в новых проектах (надеюсь личных, так как на работе будет FastAPI 😏)
* Swagger'ом как-то не проникся. Всё же TDD как-то ближе. Хотя он скорее для фронтендеров (и мобильщиков) чтобы смотреть что API выдаёт.
* В тестах немного неправильно сделал. Вообще везде, где создаю данные через api это надо делать через прямую работу с базой, но не нашёл как.  
* Сделал асинхронщину

Повторюсь, что опыт интересный, очень хочу продолжить изучение фреймворка.  

### О мотивации работать в KODE
Я успел поработать в разных компания:
* стартап на ранней стадии (ООО Нейромех, 2 года) - занимался созданием комплекса для расслабления с использованием VR  и нейроинтерфейса (UE4)
* завод (АО НПФ Микран, 1.5 года) - разрабатывал дашборд для IIoT (Django) и внутреннюю систему контроля задач (DRF)
* зарабатывающий стартап (Improvado, неделя) - исправлял баги основного проекта (Django)
* компания с одним продуктом (ИнфоТеКС, 2 месяца) - расширял функциональность приложения, исправлял баги (aiohttp)
* __Также у меня сейчас есть небольшой PET-проект, которым занимаюсь чуть больше года:__ единая база животных в приютах MuzzleBook (https://muzzlebook.ru) - руководитель и часть бэкенда (Django) пишу

На самом деле я лишь последнее время стал задумываться: "что мне нужно от компании". Всё же из Нейромеха ушёл из-за проблем с выплатами ЗП, а с Микрана, так как остался один в команде, а в перспективу набора новых сотрудников не верил.  
Однако благодаря MuzzleBook я понял, что самую большую радость доставляет когда люди пользуются результатом твоей работы. А где такое ощущение можно получить как не в заказной разработке.  
Кроме этого, у меня прям страсть руководить людьми и планировать проекты. Соответственно, "через 5 лет" надо в тимлиды идти. А где частенько будут новые проекты, в отличие от других типов кампаний. В заказной разработке.  
Также, в KODE используется python, а я его просто обожаю. Очень не хочется терять 50-60% знаний (всё же общее понимание IT останется) и учить новый язык. Конечно интересно изучить что-то новенькое в перспективе, например, Go. Но пока хочется закрепить парселтанг
