# Работа с документацией

Читайте документацию самостоятельно, без LLM-пересказов. Используйте навигацию, поиск по странице и примеры SDK. Нет необходимости читать всю спецификацию подряд.

| Шаг | Материал | Найдите ответ |
| --- | --- | --- |
| 1 | [Tools: спецификация MCP 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | Что возвращает `tools/list`? Что передаётся в `tools/call`? |
| 2 | [Tools: официальный Python SDK](https://py.sdk.modelcontextprotocol.io/servers/tools/) | Как зарегистрировать функцию, указать описание и получить схему входов? |
| 3 | [Structured Output](https://py.sdk.modelcontextprotocol.io/servers/structured-output/) | Как SDK формирует `structuredContent` и `outputSchema`? |
| 4 | [Image Content и Error Handling](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | Из чего состоит image-блок? Где находится `isError`? |
| 5 | [Running your server](https://py.sdk.modelcontextprotocol.io/run/) | Чем отличаются stdio и Streamable HTTP? |

Дополнительные справочники для алгоритмов:

- [Python 3.12: unicodedata](https://docs.python.org/3.12/library/unicodedata.html).
- [Python 3.12: hashlib](https://docs.python.org/3.12/library/hashlib.html).
- [Python 3.12: io](https://docs.python.org/3.12/library/io.html).
- [Pillow: Image](https://pillow.readthedocs.io/en/stable/reference/Image.html).

Веб-документация SDK обновляется. Для курса зафиксирован `mcp==2.3.0`: сверяйте примеры с установленной версией, при расхождении обращайтесь к преподавателю. В исходном коде установленного пакета и через `help()` можно проверить актуальные сигнатуры. Не переключайтесь самостоятельно на другую версию.

В `SUBMISSION.md` ответьте своими словами на четыре вопроса. Для каждого укажите ссылку на раздел документации и имя функции/класса в собственном коде:

1. Как функция становится MCP-инструментом и откуда берётся схема её аргументов?
2. Чем JSON-строка в тексте отличается от структурированного результата? Как это реализовано у вас?
3. Как клиент узнаёт, что результат содержит изображение, и как получает его байты?
4. Чем ошибка выполнения инструмента отличается от успешного результата и ошибки протокола?

На каждый вопрос достаточно 2–4 предложений. Проверяется связь документации с вашей реализацией, а не объём текста.
